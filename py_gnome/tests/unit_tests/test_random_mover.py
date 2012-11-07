"""
unittests for random mover

designed to be run with py.test
"""
import datetime

import numpy as np

import gnome
from gnome import movers
from gnome import basic_types, spill
from gnome.utilities import time_utils 
from gnome.utilities import projections


import pytest


def test_exceptions():
    """
    Test ValueError exception thrown if improper input arguments
    """
    with pytest.raises(ValueError):
        movers.RandomMover(diffusion_coef=0)


class TestRandomMover():
    """
    gnome.RandomMover() test

    """
    num_le = 5
    start_pos = np.zeros((num_le,3), dtype=basic_types.world_point_type)
    rel_time = datetime.datetime(2012, 8, 20, 13)    # yyyy/month/day/hr/min/sec
    model_time = time_utils.sec_to_date(time_utils.date_to_sec(rel_time) + 1)
    time_step = 15*60 # seconds

    pSpill = spill.PointReleaseSpill(num_le, start_pos, rel_time, persist=-1)

    mover = movers.RandomMover()
    
    def reset_pos(self):
        self.pSpill['positions'] = (0.,0.,0.)
        print self.pSpill['positions']
    
    def test_string_representation_matches_repr_method(self):
        assert repr(self.mover) == 'Random Mover'
        assert str(self.mover) == 'Random Mover'

    def test_id_matches_builtin_id(self):
        assert id(self.mover) == self.mover.id

    def test_get_move(self):
        """
        Test the get_move(...) results in RandomMover
        """
        self.pSpill.prepare_for_model_step(self.model_time, self.time_step)
        self.mover.prepare_for_model_step(self.model_time, self.time_step)

        # make sure clean up is happening fine
        num_steps = 4
        delta = np.zeros((num_steps,self.pSpill.num_LEs), dtype=basic_types.world_point)
        delta = np.zeros((num_steps,self.pSpill.num_LEs), dtype=basic_types.world_point) 
        for ix in range(0,num_steps):
            curr_time = time_utils.sec_to_date(time_utils.date_to_sec(self.model_time)+(self.time_step*ix))
            print "Time step [sec]: " + str( time_utils.date_to_sec(curr_time)-time_utils.date_to_sec(self.model_time))
            delta[ix] = self.mover.get_move(self.pSpill, self.time_step, curr_time)
            
        print delta
        print "------"
        deltaV = delta.view(dtype=np.double).reshape(-1,3)
        print deltaV
        print "------"
        print np.mean(deltaV, axis=0)
        #mag_delta = np.apply_along_axis(np.linalg.norm, 1, deltaV)
        print "------"
       
    def test_change_diffusion_coef(self):
        self.mover.diffusion_coef = 200000
        print self.mover.diffusion_coef
        assert self.mover.diffusion_coef == 200000 


class Test_variance:
    num_le = 10
    start_time = datetime.datetime(2012,11,10,0)
    time_step = 360 #seconds -- 6 minutes
    spill = gnome.spill.PointReleaseSpill(num_le, (0.0,0.0,0.0), start_time)

    def test_variance1(self):
        """
        After a few timesteps the variance of the particle positions should be
        similar to the computed value: var = Dt
        """
        self.spill.reset()

        rand = movers.RandomMover(diffusion_coef=100000)

        model_time = self.start_time
        for i in range(100):# run for ten steps
            model_time += datetime.timedelta(seconds=self.time_step)
            print model_time
            rand.prepare_for_model_step(model_time, self.time_step)
            delta = rand.get_move(self.spill, self.time_step, model_time)
            print "delta:", delta
            self.spill['positions'] += delta.view(dtype=basic_types.world_point_type).reshape((-1,3))

        assert False

       
if __name__=="__main__":
    tw = TestRandomMover()
    tw.test_get_move()
    tw.test_change_diffusion_coef()