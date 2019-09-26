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
        self.action_space = gym.spaces.Discrete(3)  # �g���[�_�[�̍s���̑I������[Buy, Sell, Stay]
        self.observation_space = gym.spaces.Box(    
            low = 0.,          # �ŏ��l
            high = 10000.,     # �ő�l
            shape=(6,)         # �ϑ��l
        )
        self.reward_range = [-500000., 500000.] 
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
        rate = self.trade_sys.tick["close"]
        # �A�g���[�h�A�N�V�������s( buy, sell, stay )
        if action == 0:
            self.trade_sys.order("BUY", rate, trade_system.AMOUNT_MAX)
        elif action == 1:
            self.trade_sys.order("SELL", rate, trade_system.AMOUNT_MAX)
        else:
            pass
        # �Btick���X�V
        self.trade_sys.update_tick()

        observation = self._observe()
        reward = self._get_reward()
        self.done = self._is_done()
        return observation, reward, self.done, {}

    def _render(self, mode='human', close=False):
        # human �̏ꍇ�̓R���\�[���ɏo�́Bansi�̏ꍇ�� StringIO ��Ԃ�
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        close =  str("{0:.2f}".format(self.trade_sys.tick.close))
        profit =  str("{0:.2f}".format(self.trade_sys.profit))
        inprofit =  str("{0:.2f}".format(self.trade_sys.inprofit))
        dir = str(self.trade_sys.trade_pos.dir)
        outfile.write( close+'\t\t'+profit+'\t\t'+inprofit+'\t\t'+dir+'\n')
        return outfile

    def _close(self):
        pass

    def _seed(self, seed=None):
        pass

    def _get_reward(self):
        # ��V��Ԃ��B
        reward = self.trade_sys.profit + self.trade_sys.inprofit
        self.reward_pre = reward
        return reward

    def _observe(self):
        cols = ['mv_avrg_div', 'RSI', 'tenkan_div', 'base', 'senkou1', 'senkou2']
        observation = np.array(self.trade_sys.tick[cols])
        return observation

class trade_train(trade):
    def _is_done(self):
        if self.trade_sys.tick_num == (len(self.trade_sys.chart.index) - 1) :
            return True
        else:
            return False

class trade_test(trade):
    def _is_done(self):
        if self.trade_sys.tick_num == (len(self.trade_sys.chart.index) - 1) :
            return True
