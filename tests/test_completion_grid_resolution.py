"""Grid mapping, training support and held-out label isolation."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('completion_grid_resolution',ROOT/'52_completion_grid_resolution.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


class CompletionGridTests(unittest.TestCase):
    def test_outer_edges_and_internal_boundaries(self):
        self.assertEqual(lesson.grid_cell([120,80],12,8),95)
        self.assertEqual(lesson.grid_cell([20,20],6,4),7)
        self.assertEqual(lesson.grid_cell([45,30],3,2),1)
        self.assertEqual(lesson.grid_cell([45,30],6,4),8)
        for point,nx,ny in [([121,0],6,4),([0,0],0,4),([float('nan'),0],6,4)]:
            with self.assertRaises(ValueError):lesson.grid_cell(point,nx,ny)

    def test_empty_cells_fall_back_to_training_reference(self):
        rows=[{'cell':0,'completed':1},{'cell':1,'completed':0}]
        model=lesson.fit_cells(rows,6,20)
        self.assertEqual(model['probabilities'][2],.5)
        self.assertEqual(sum(model['attempts_by_cell']),2)

    def test_one_cell_reproduces_global_training_rate(self):
        rows=[{'cell':0,'completed':y} for y in [1,1,1,0]]
        self.assertAlmostEqual(lesson.fit_cells(rows,1,20)['probabilities'][0],.75)

    def test_held_out_labels_do_not_change_its_model_or_predictions(self):
        rows=[{'match_id':m,'id':str(i),'start':[45,30],'completed':y}
              for m,ys in [(1,[0,1]),(2,[1,1]),(3,[0,1]),(4,[0,1])] for i,y in enumerate(ys)]
        first=lesson.evaluate_grid(rows,[1,2,3,4],3,2,20)
        changed=copy.deepcopy(rows)
        for row in changed:
            if row['match_id']==1:row['completed']=1
        second=lesson.evaluate_grid(changed,[1,2,3,4],3,2,20)
        self.assertEqual(first['folds'][0]['model'],second['folds'][0]['model'])
        self.assertEqual([r['probability'] for r in first['predictions'] if r['match_id']==1],
                         [r['probability'] for r in second['predictions'] if r['match_id']==1])
