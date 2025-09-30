'''
Script used to study Jpsi leakage in central q2 bin
'''
import os
import mplhep
import pandas            as pnd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from rx_selection           import selection as sel
from rx_data.rdf_getter     import RDFGetter

from dmu.logging.log_store  import LogStore

log=LogStore.add_logger('rx_plot:leakage')
# --------------------------------
class Data:
    '''
    Data class
    '''
    plt.style.use(mplhep.style.LHCb2)
    cache_dir : str
    plots_dir : str

    jpsi    = 'Bu_JpsiK_ee_eq_DPC'
    psi2    = 'Bu_psi2SK_ee_eq_DPC'

    trigger = 'Hlt2RD_BuToKpEE_MVA'
    q2bin   = 'central'
    columns = [
            'nbrem',
            'B_M',
            'B_M_brem_track_2',
            'B_M_smr_brem_track_2',
            'Jpsi_M',
            'Jpsi_M_brem_track_2',
            'Jpsi_M_smr_brem_track_2',
            ]

    d_latex = {
            jpsi : r'$B^+\to K^+ J/\psi(\to ee)$',
            psi2 : r'$B^+\to K^+ \psi(2S)(\to ee)$'}
# --------------------------------
def _initialize():
    ana_dir        = os.environ['ANADIR']
    Data.cache_dir = '/tmp/cache/rx_plots/leakage'
    Data.plots_dir = f'{ana_dir}/plots/leakage'

    os.makedirs(Data.cache_dir, exist_ok=True)
    os.makedirs(Data.plots_dir, exist_ok=True)
# --------------------------------
def _get_df(sample : str) -> pnd.DataFrame:
    out_path = f'{Data.cache_dir}/data_{sample}_{Data.trigger}_{Data.q2bin}.json'
    if os.path.isfile(out_path):
        log.debug(f'Loading data from: {out_path}')

        df = pnd.read_json(out_path)

        return df

    gtr = RDFGetter(sample=sample, trigger=Data.trigger)
    rdf = gtr.get_rdf(per_file=False)

    d_sel = sel.selection(trigger=Data.trigger, q2bin=Data.q2bin, process=sample)
    d_sel['q2']   = '(1)'
    d_sel['mass'] = '(1)'

    for cut_name, cut_expr in d_sel.items():
        rdf = rdf.Filter(cut_expr, cut_name)

    data = rdf.AsNumpy(Data.columns)
    df   = pnd.DataFrame(data)
    df   = _define_columns(df)

    log.info(f'Saving data to: {out_path}')
    df.to_json(out_path, indent=4)

    return df
# --------------------------------
def _define_columns(df : pnd.DataFrame) -> pnd.DataFrame:
    df['qsq_org' ] = df['Jpsi_M'                 ] ** 2 / 1e6
    df['qsq_cor' ] = df['Jpsi_M_brem_track_2'    ] ** 2 / 1e6
    df['qsq_smr' ] = df['Jpsi_M_smr_brem_track_2'] ** 2 / 1e6

    df['mass_org'] = df['B_M'                    ]
    df['mass_cor'] = df['B_M_brem_track_2'       ]
    df['mass_smr'] = df['B_M_smr_brem_track_2'   ]

    l_drop = [ col for col in Data.columns if col not in ['nbrem'] ]
    df     = df.drop(columns=l_drop)

    return df
# --------------------------------
def _plot_b_mass(df : pnd.DataFrame, kind : str) -> None:
    maxq = 6.0
    if   kind == 'original':
        df = df[(df.qsq_org  < maxq) & (df.qsq_org  >    1)]
        df = df[(df.mass_org < 6000) & (df.mass_org > 4500)]
    elif kind == 'corrected and smeared':
        df = df[(df.qsq_smr  < maxq) & (df.qsq_smr  >    1)]
        df = df[(df.mass_smr < 6000) & (df.mass_smr > 4500)]
    elif kind == 'corrected':
        df = df[(df.qsq_cor  < maxq) & (df.qsq_cor  >    1)]
        df = df[(df.mass_cor < 6000) & (df.mass_cor > 4500)]
    else:
        raise ValueError

    nentries = len(df)

    plt.hist(df['mass_org'], range=(4000, 5500), bins=30, alpha=0.7      , label='Original'             , color='gray')
    plt.hist(df['mass_cor'], range=(4000, 5500), bins=30, histtype='step', label='Corrected'            , color='blue')
    plt.hist(df['mass_smr'], range=(4000, 5500), bins=30, histtype='step', label='Corrected and smeared', color='red')
    plt.title(f'Entries: {nentries}, Cut on: {kind}')
    plt.legend()
    plt.xlabel(r'M$(B^+)$')

    name = kind.replace(' ', '_')
    plt.savefig(f'{Data.plots_dir}/{name}.png')
    plt.close()
# --------------------------------
def _check_q2_leakage(sample : str, nbrem : int) -> None:
    df = _get_df(sample=sample)

    if nbrem != -1:
        df = df[df['nbrem'] == nbrem]
    
    nbrem_label = str(nbrem) if nbrem != -1 else 'all'

    fig, ax = plt.subplots(figsize=[15,10])

    df['qsq_org'].plot.hist(bins=60, range=[-3, 22], density=True, label='Original' , alpha   =   0.2, color='black')
    df['qsq_cor'].plot.hist(bins=60, range=[-3, 22], density=True, label='Corrected', histtype='step', color='blue' )
    df['qsq_smr'].plot.hist(bins=60, range=[-3, 22], density=True, label='Smeared'  , histtype='step', color='red'  )

    latex = Data.d_latex[sample]

    fig.legend(loc='upper left', bbox_to_anchor=(0.2, 0.9))
    plt.title(f'{latex}; Brem={nbrem_label}')
    ax.set_ylim(top=0.05)
    ax.set_xlabel(r'$q^2$[GeV$/c^2$]')
    ax.set_ylabel('Normalized')
    ax.axvline(x= 6, ls=':', color='green')
    ax.axvline(x=15, ls=':', color='green')
    ax.axvline(x=22, ls=':', color='green')
    plot_path = f'{Data.plots_dir}/{sample}_{nbrem_label}.png'

    log.info(f'Saving to:{plot_path}')
    plt.savefig(plot_path)
    plt.close()
# --------------------------------
def main():
    '''
    Start here
    '''
    _initialize()

    #_compare_mass_cuts()
    #_check_q2_leakage(sample=Data.jpsi)
    for nbrem in [-1, 0, 1, 2]:
        _check_q2_leakage(sample=Data.psi2, nbrem = nbrem)
        _check_q2_leakage(sample=Data.jpsi, nbrem = nbrem)
# --------------------------------
if __name__ == '__main__':
    main()
