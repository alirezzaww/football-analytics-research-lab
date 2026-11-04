"""Lesson 52: vary completion-model grid resolution with all other rules fixed."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def grid_cell(point, nx, ny):
    if any(type(n) is not int or n <= 0 for n in (nx, ny)):
        raise ValueError('Grid dimensions must be positive integers')
    if not isinstance(point, list) or len(point) < 2 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in point[:2]):
        raise ValueError('Need finite start coordinates')
    x, y = point[:2]
    if not 0 <= x <= 120 or not 0 <= y <= 80:
        raise ValueError('Start outside normalized pitch')
    return min(int(y/80*ny),ny-1)*nx + min(int(x/120*nx),nx-1)


def fit_cells(rows, n_cells, strength):
    if not rows or strength <= 0:
        raise ValueError('Need fitting observations and positive smoothing')
    n = [0]*n_cells; success = [0]*n_cells
    for row in rows:
        n[row['cell']] += 1; success[row['cell']] += row['completed']
    reference = sum(success)/len(rows)
    return {'training_attempts': len(rows), 'global_training_rate': reference,
            'attempts_by_cell': n, 'completions_by_cell': success,
            'probabilities': [(success[i]+strength*reference)/(n[i]+strength) for i in range(n_cells)]}


def evaluate_grid(rows, match_ids, nx, ny, strength):
    spec = importlib.util.spec_from_file_location('grid_completion_metrics', ROOT / '47_first_pass_completion_model.py')
    scorer = importlib.util.module_from_spec(spec); spec.loader.exec_module(scorer)
    mapped = [{**r,'cell':grid_cell(r['start'],nx,ny)} for r in rows]
    folds = []; predictions = []
    for omitted in match_ids:
        train = [r for r in mapped if r['match_id'] != omitted]
        model = fit_cells(train,nx*ny,strength)
        check = [{'match_id': r['match_id'],'id': r['id'],'completed':r['completed'],
                  'cell':r['cell'],'probability':model['probabilities'][r['cell']]} for r in mapped if r['match_id']==omitted]
        folds.append({'held_out_match_id':omitted,'training_match_ids':[m for m in match_ids if m!=omitted],
                      'model':model,'metrics':scorer.score_probabilities(check,'probability')})
        predictions.extend(check)
    return {'nx':nx,'ny':ny,'cells':nx*ny,'folds':folds,'predictions':predictions,
            'pooled_metrics':scorer.score_probabilities(predictions,'probability')}


def build_evidence():
    protocol_path = ROOT / 'data/52_completion_grid_protocol.json'
    protocol = json.loads(protocol_path.read_text())
    source_path = ROOT / 'data/45_failed_pass_value_evidence.json'
    source = json.loads(source_path.read_text())
    reference_path = ROOT / 'data/48_completion_match_cv_evidence.json'
    reference = json.loads(reference_path.read_text())
    rows = [{'match_id':r['match_id'],'id':r['id'],'start':r['start'],'completed':int(r['pass_outcome'] is None)}
            for r in source['passes'] if r['pass_outcome'] is None or r['pass_outcome'] in ('Incomplete','Out','Pass Offside')]
    candidates = [evaluate_grid(rows,reference['match_ids'],nx,ny,protocol['smoothing_strength']) for nx,ny in protocol['grids']]
    original = next(c for c in candidates if (c['nx'],c['ny'])==(6,4))
    assert original['pooled_metrics'] == reference['pooled_zone_metrics']
    constant = next(c for c in candidates if (c['nx'],c['ny'])==(1,1))
    assert math.isclose(constant['pooled_metrics']['log_loss'],reference['pooled_baseline_metrics']['log_loss'])
    return {'source_path':source_path.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
            'reference_path':reference_path.relative_to(ROOT).as_posix(),'reference_sha256':hashlib.sha256(reference_path.read_bytes()).hexdigest(),
            'protocol_path':protocol_path.relative_to(ROOT).as_posix(),'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            'match_ids':reference['match_ids'],'input_passes':rows,'candidates':candidates,'scope':protocol['purpose']}


def main():
    evidence = build_evidence()
    (ROOT / 'data/52_completion_grid_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    import matplotlib.pyplot as plt
    candidates = evidence['candidates']
    fig,axes=plt.subplots(1,2,figsize=(11,5))
    labels=[f"{c['nx']}×{c['ny']}\n{c['cells']} {'cell' if c['cells']==1 else 'cells'}" for c in candidates]
    axes[0].bar(labels,[c['pooled_metrics']['log_loss'] for c in candidates],color=['#8c9397','#24658a','#b77516','#446b57'])
    axes[0].set_title('Pooled held-out probability error')
    axes[0].set_ylabel('Log loss · lower is better')
    for i,c in enumerate(candidates):
        axes[0].text(i,c['pooled_metrics']['log_loss'],f"{c['pooled_metrics']['log_loss']:.4f}",ha='center',va='bottom',fontsize=9)
    means=[sum(sum(f['model']['attempts_by_cell']) for f in c['folds'])/(len(c['folds'])*c['cells']) for c in candidates]
    axes[1].bar(labels,means,color='#24658a')
    axes[1].set_title('Fitting data spread across more cells')
    axes[1].set_ylabel('Mean fitting passes per cell across folds')
    for ax in axes:
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('How many pitch zones should our completion model use?\nSame passes, smoothing strength and whole-match checks',fontsize=14)
    fig.text(.5,.02,'Grid resolution is a modelling choice. Results use inspected development data and do not establish a universal best grid.\nOnly start coordinates are prediction features. Data: StatsBomb Open Data.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.1,1,.85])
    fig.savefig(ROOT / 'figures/54_completion_grid_resolution.png',dpi=160)
    plt.show()
    for c in candidates:
        print(c['nx'],c['ny'],c['pooled_metrics'])


if __name__=='__main__':
    main()
