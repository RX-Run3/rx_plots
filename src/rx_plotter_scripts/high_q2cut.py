'''
Script used to study effect of different cuts on q2
to get signal in high q2 bin
'''
import os
import argparse

import numpy
import mplhep
import pandas            as pnd
import matplotlib.pyplot as plt

from ROOT                  import RDataFrame
from rx_data.rdf_getter    import RDFGetter
from rx_data.rdf_getter12  import RDFGetter12
from rx_selection          import selection as sel
from dmu.logging.log_store import LogStore

log=LogStore.add_logger('rx_plots:high_q2cut')
# ---------------------------
class Data:
    '''
    Data class
    '''
    plt_dir : str
    sample  : str
    run     : str
    trigger : str

    d_samples = {
            'data_ss' : 'DATA*',
            'buhsee'  : 'Bu_JpsiX_ee_eq_JpsiInAcc',
            'bdhsee'  : 'Bd_JpsiX_ee_eq_JpsiInAcc',
            'bshsee'  : 'Bs_JpsiX_ee_eq_JpsiInAcc',
            'bukee'   : 'Bu_Kee_eq_btosllball05_DPC',
            'bukjpee' : 'Bu_JpsiK_ee_eq_DPC',
            'bukpsee' : 'Bu_psi2SK_ee_eq_DPC'}

    d_latex   = {
            'DATA*'                      : 'SS data',
            'Bu_JpsiX_ee_eq_JpsiInAcc'   : r'$B^+\to H_s c\bar{c}(\to e^+e^-)$',
            'Bd_JpsiX_ee_eq_JpsiInAcc'   : r'$B^0\to H_s c\bar{c}(\to e^+e^-)$',
            'Bs_JpsiX_ee_eq_JpsiInAcc'   : r'$B_s\to H_s c\bar{c}(\to e^+e^-)$',
            'Bu_Kee_eq_btosllball05_DPC' : r'$B^+\to K^+e^+e^-$',
            'Bu_JpsiK_ee_eq_DPC'         : r'$B^+\to K^+J/\psi(\to e^+e^-)$',
            'Bu_psi2SK_ee_eq_DPC'        : r'$B^+\to K^+\psi(2S)(\to e^+e^-)$'}

    q2bin   = 'high'
    bmass   = 'B_Mass_smr'
    plt.style.use(mplhep.style.LHCb2)

    min_q2  = 10
    max_q2  = 24

    cut_min = 14.3
    cut_max = 22.0

    mass_rng= [4500, 6000]

    l_q2var = ['q2_true', 'q2_smr', 'q2_track', 'q2_dtf', 'nbrem', 'B_Mass_smr']
# ---------------------------
def _parse_args():
    parser = argparse.ArgumentParser(description='Used to perform several operations on TCKs')
    parser.add_argument('-s', '--sample', type=str, help='MC sample', required=True, choices=list(Data.d_samples))
    parser.add_argument('-r', '--run'   , type=str, help='Run from which to plot', default='run3', choices=['run12', 'run3'])
    args = parser.parse_args()

    sample     = args.sample
    Data.sample= Data.d_samples[sample]
    Data.run   = args.run
# ---------------------------
def _initialize():
    ana_dir = os.environ['ANADIR']
    plt_dir = f'{ana_dir}/plots/high_q2/{Data.sample}'

    os.makedirs(plt_dir, exist_ok=True)

    if Data.sample.startswith('DATA'):
        Data.trigger = 'Hlt2RD_BuToKpEE_SameSign_MVA'
    else:
        Data.trigger = 'Hlt2RD_BuToKpEE_MVA'

    Data.plt_dir = plt_dir
# ---------------------------
def _get_rdf() -> RDataFrame:
    if Data.run == 'run3':
        return _get_run3_rdf()

    if Data.run == 'run12':
        return _get_run12_rdf()

    raise ValueError(f'Invalid run: {Data.run}')
# ---------------------------
def _get_run3_rdf() -> RDataFrame:
    gtr = RDFGetter(sample=Data.sample, trigger=Data.trigger)
    rdf = gtr.get_rdf()

    d_sel       = sel.selection(trigger=Data.trigger, q2bin=Data.q2bin, process=Data.sample)
    d_sel['q2'] = '(1)'

    for cut_name, cut_value in d_sel.items():
        rdf = rdf.Filter(cut_value, cut_name)

    if log.getEffectiveLevel() < 20:
        rep = rdf.Report()
        rep.Print()

    return rdf
# ---------------------------
def _get_run12_rdf() -> RDataFrame:
    gtr = RDFGetter12(
            sample = Data.sample,
            trigger= Data.trigger,
            dset   = 'all')

    rdf = gtr.get_rdf()
    #rdf = rdf.Filter('BDT_cmb > 0.9 && BDT_prc > 0.8')
    rdf = rdf.Filter('nbrem <= 2')

    return rdf
# ---------------------------
def _reformat_q2(df : pnd.DataFrame) -> pnd.DataFrame:
    l_col = [ col for col in df.columns if col.startswith('q2') ]

    for col in l_col:
        df[col] = df[col] / 1e6

    return df
# ---------------------------
def _rdf_to_df(rdf : RDataFrame) -> pnd.DataFrame:
    if 'data' in Data.sample:
        l_q2var = [ var for var in Data.l_q2var if 'true' not in var ]
    else:
        l_q2var = Data.l_q2var

    data = rdf.AsNumpy(l_q2var)
    df   = pnd.DataFrame(data)
    df   = _reformat_q2(df=df)

    return df
# ---------------------------
def _plot(rdf : RDataFrame) -> None:
    df   = _rdf_to_df(rdf)
    for brem, df_brem in df.groupby('nbrem'):
        #_plot_reco_q2(brem, df=df_brem)
        _plot_true_q2(brem, df=df_brem)

    #_plot_reco_q2('all', df)
    _plot_true_q2('all', df)
# ---------------------------
def _plot_eff(arr_val : numpy.ndarray, color : str, ax) -> None:
    sorted_data = numpy.sort(arr_val)
    eff         = 1 - numpy.arange(1, len(arr_val) + 1) / len(arr_val)

    ax.plot(sorted_data, eff, color=color)
# ---------------------------
def _plot_reco_q2(brem : int, df : pnd.DataFrame) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(30, 10))

    ax1.hist(df['q2_smr'  ], bins=60, range=[0, Data.max_q2], density=True, label='$q^2$'        , alpha = 0.2, color='blue' )
    ax1.hist(df['q2_dtf'  ], bins=60, range=[0, Data.max_q2], density=True, label='$q^2_{DTF}$'  , alpha = 0.2, color='green')
    ax1.hist(df['q2_track'], bins=60, range=[0, Data.max_q2], density=True, label='$q^2_{track}$', alpha = 0.2, color='red'  )

    df_smr=df[(df.q2_smr   > 15) & (df.q2_smr   < 22)                     ]
    df_dtf=df[(df.q2_dtf   > 15) & (df.q2_dtf   < 22) & (df.q2_smr   < 22)]
    df_trk=df[(df.q2_track > 15) & (df.q2_track < 22)                     ]

    ax2.hist(df_smr[Data.bmass], bins=60, range=Data.mass_rng, label='$q^2$'        , alpha   =   0.2, color='blue' )
    ax2.hist(df_dtf[Data.bmass], bins=60, range=Data.mass_rng, label='$q^2_{DTF}$'  , histtype='step', color='green')
    ax2.hist(df_trk[Data.bmass], bins=60, range=Data.mass_rng, label='$q^2_{track}$', histtype='step', color='red'  )

    arr_q2smr = df[(df.q2_smr   < 22)                     ]['q2_smr'  ].to_numpy()
    arr_q2dtf = df[(df.q2_dtf   < 22) & (df.q2_smr   < 22)]['q2_dtf'  ].to_numpy()
    arr_q2trk = df[(df.q2_track < 22)                     ]['q2_track'].to_numpy()

    ax3= ax1.twinx()
    ax1.set_ylim(0, 0.20)
    ax3.set_ylim(0, 0.40)
    ax3.set_xlim(Data.min_q2, Data.max_q2)

    _plot_eff(arr_q2smr, color='blue' , ax=ax3)
    _plot_eff(arr_q2dtf, color='green', ax=ax3)
    _plot_eff(arr_q2trk, color='red'  , ax=ax3)

    ax3.tick_params(axis='y', labelcolor='green')
    ax3.set_ylabel('Efficiency', color='green')
    ax1.set_xlabel('$q^2$[GeV$/c^{2}$]')
    ax2.set_xlabel('$M(B^+)$[MeV$/c^{2}$]')

    ax1.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))
    ax2.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))

    title = _get_title(brem=brem)

    fig.suptitle(title, fontsize=40)
    ax1.axvline(x=15  , c='black', ls=':')
    ax2.axvline(x=5280, c='black', ls=':')

    plt.grid()
    plt.savefig(f'{Data.plt_dir}/q2_{brem}_{Data.run}.png')
    plt.close()
# ---------------------------
def _plot_true_q2(brem : int, df : pnd.DataFrame) -> None:
    if 'data' in Data.sample:
        return

    df_raw = df

    cut_value = 14.3
    df_trk = df_raw[df_raw['q2_track'] > cut_value ]
    df_smr = df_raw[df_raw['q2_smr'  ] > cut_value ]
    df_dtf = df_raw[df_raw['q2_dtf'  ] > cut_value ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(30, 10))

    ax1.hist(df_raw['q2_true'], bins=60, range=[0, Data.max_q2], density=False, label=r'No cut'              , alpha   =   0.2, color='blue'  )
    ax1.hist(df_smr['q2_true'], bins=60, range=[0, Data.max_q2], density=False, label=r'Cut on $q^2$'        , histtype='step', color='green' )
    ax1.hist(df_trk['q2_true'], bins=60, range=[0, Data.max_q2], density=False, label=r'Cut on $q^2_{track}$', histtype='step', color='red'   )
    ax1.hist(df_dtf['q2_true'], bins=60, range=[0, Data.max_q2], density=False, label=r'Cut on $q^2_{DTF}$'  , histtype='step', color='orange')

    ax2.hist(df_raw[Data.bmass], bins=60, range=Data.mass_rng, label=r'No cut'              , alpha   =   0.2, color='blue'  )
    ax2.hist(df_smr[Data.bmass], bins=60, range=Data.mass_rng, label=r'Cut on $q^2$'        , histtype='step', color='green' )
    ax2.hist(df_trk[Data.bmass], bins=60, range=Data.mass_rng, label=r'Cut on $q^2_{track}$', histtype='step', color='red'   )
    ax2.hist(df_dtf[Data.bmass], bins=60, range=Data.mass_rng, label=r'Cut on $q^2_{DTF}$'  , histtype='step', color='orange')

    ax1.axvline(cut_value, label='Cut', ls=':', color='black')

    ax1.legend(loc='upper right', bbox_to_anchor=(0.9, 1.0))
    ax2.legend(loc='upper right', bbox_to_anchor=(0.9, 1.0))

    ax1.set_xlabel(r'$q^2_{True}$')
    ax2.set_xlabel(r'$M_{corr}(K^+e^+e^-)$')

    title = _get_efficiencies_title(
            df_raw=df,
            df_smr=df_smr,
            df_dtf=df_dtf,
            df_trk=df_trk)

    fig.suptitle(title, fontsize=40)

    if isinstance(brem, int):
        brem = f'{brem:.0f}'

    plot_path = f'{Data.plt_dir}/true_q2_{Data.run}_{brem}.png'
    log.info(f'Saving to: {plot_path}')

    plt.grid()
    plt.savefig(plot_path)
    plt.close()
# ---------------------------
def _get_efficiencies_title(
        df_raw : pnd.DataFrame,
        df_smr : pnd.DataFrame,
        df_dtf : pnd.DataFrame,
        df_trk : pnd.DataFrame) -> str:

    tot = len(df_raw)
    smr = len(df_smr)
    dtf = len(df_dtf)
    trk = len(df_trk)

    eff_smr = smr/tot * 100
    eff_dtf = dtf/tot * 100
    eff_trk = trk/tot * 100

    title = (
            f'$\\varepsilon_{{ORG}}={eff_smr:.0f}$%; '
            f'$\\varepsilon_{{DTF}}={eff_dtf:.0f}$%; '
            f'$\\varepsilon_{{TRK}}={eff_trk:.0f}$%'
            )

    return title
# ---------------------------
def _get_title(brem : str) -> str:
    latex = Data.d_latex[Data.sample]

    return f'Brem = {brem}; {latex}'
# ---------------------------
def main():
    '''
    Start here
    '''
    _parse_args()
    _initialize()

    rdf = _get_rdf()

    _plot(rdf=rdf)
# ---------------------------
if __name__ == '__main__':
    main()
