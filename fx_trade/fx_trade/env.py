# coding: utf-8
import sys

import pandas as pd
import gym
import numpy as np
import gym.spaces
import csv
from . import trade_system

class trade(gym.Env):
    def __init__(self):
        super().__init__()
        # action_space, observation_space, reward_range ��ݒ肷��
        self.action_space = gym.spaces.Discrete(3)  # �g���[�_�[�̍s���̑I������
        self.observation_space = gym.spaces.Box(    
            low = 0.,          # �ŏ��l
            high = 10000.,     # �ő�l
            shape=(6,)         # �ϑ��l
        )
        self.reward_range = [-500000., 500000.] # WIN or LOSE
        self.trade_sys = trade_system.trade_system()
        self._reset()

    def _reset(self):
        # ���X�̕ϐ�������������
        self.done = False
        self.trade_sys.reset()
        return self._observe()

    def _step(self, action):
        # 1�X�e�b�v�i�߂鏈�����L�q�B�߂�l�� observation, reward, done(�Q�[���I��������), info(�ǉ��̏��̎���)
        # �@���[�g�擾
        rate = self.trade_sys.tick_now["rate_ed"]
        # �A�g���[�h�A�N�V�������s( buy, sell, stay )
        if action == 0:
            self.trade_sys.order("BUY", rate, trade_system.AMOUNT_MAX)
        elif action == 1:
            self.trade_sys.order("SELL", rate, trade_system.AMOUNT_MAX)
        else:
            pass
        # �Btick������
        self.trade_sys.update_tick()
        # �C�܂݉v�v�Z
        rate = self.trade_sys.tick_now["rate_ed"]
        self.trade_sys.calc_inprofit(rate)
        observation = self._observe()
        reward = self._get_reward()
        self.done = self._is_done()
        return observation, reward, self.done, {}

    def _render(self, mode='human', close=False):
        # human �̏ꍇ�̓R���\�[���ɏo�́Bansi�̏ꍇ�� StringIO ��Ԃ�
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        outfile.write( str(self.trade_sys.tick_now["rate_ed"])+"\t"+str(self.trade_sys.profit)+",\t"+str(self.trade_sys.inprofit)+",\t"+str(self.trade_sys.trade_pos.dir)+'\n')
        return outfile

    def _close(self):
        pass

    def _seed(self, seed=None):
        pass

    def _get_reward(self):
        # ��V��Ԃ��B
        reward = (self.trade_sys.profit - self.trade_sys.profit_pre) + (self.trade_sys.inprofit - self.trade_sys.inprofit_pre)
        return reward

    def _observe(self):
        center = (self.trade_sys.tick_now["rate_st"] + self.trade_sys.tick_now["rate_ed"])/2
        rate_st = self.trade_sys.tick_now["rate_st"]/center
        rate_hi = self.trade_sys.tick_now["rate_hi"]/center
        rate_lo = self.trade_sys.tick_now["rate_lo"]/center
        rate_ed = self.trade_sys.tick_now["rate_ed"]/center
        production = self.trade_sys.tick_now["production"]
        pos_amount = self.trade_sys.trade_pos.amount
        observation = np.array([rate_st, rate_hi, rate_lo, rate_ed, production, pos_amount])
        return observation

class trade_train(trade):
    def _is_done(self):
        if self.trade_sys.now == (len(self.trade_sys.hist_data.index) - 1) :
            return True
        if self.trade_sys.profit != self.trade_sys.profit_pre:
            return True
        else:
            return False

class trade_test(trade):
    def _is_done(self):
        if self.trade_sys.now == (len(self.trade_sys.hist_data.index) - 1) :
            return True
