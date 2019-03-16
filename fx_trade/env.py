# coding: utf-8
import sys

import pandas as pd
import gym
import numpy as np
import gym.spaces
import csv

PATH = './data/USDJPY1_201810.csv'
AMOUNT_MAX = 1


class trade_pos():
    def __init__(self):
        self.dir = "NONE"
        self.average_cost = 0
        self.amount = 0



class trade_system():
    def __init__(self):
        self.leverage   = 25        # ���o25�{
        self.spread     = 0.005     # �X�v���b�h�Œ� 0.005pips

        self.feature = ["ymd", "hm", "rate_st", "rate_hi", "rate_lo", "rate_ed", "production"]
        self.hist_data = pd.read_csv(PATH, names=self.feature )
        self.now = 0
        self.tick_now = self.hist_data.iloc[self.now]

        self.reset()

    def reset(self):
        self.profit     = 0         # ���v
        self.profit_pre = 0 
        self.inprofit       = 0         # �܂ݑ��v
        self.inprofit_pre   = 0
        self.trade_pos  = trade_pos()   # �|�W�V����

    def update_tick(self):
        self.now += 1
        if self.now < len(self.hist_data.index):
            self.tick_now = self.hist_data.iloc[self.now]

    # ����
    def order(self, dir, rate, amount):
        # dir ; ����["BUY", "SELL", "NONE"]
        # rate  : �������i
        # amount: ��������
        if dir == "BUY":
            rate += self.spread
        elif dir == "SELL":
            rate -= self.spread

        amount = amount * 10000 * self.leverage
        if self.trade_pos.amount == 0:      # �@�|�W�V���������̏ꍇ
            self.trade_pos.average_cost = rate  # �擾���ω��i = �������i
            self.trade_pos.amount = amount      # �ۗL����     = ��������
            self.trade_pos.dir = dir
        elif self.trade_pos.dir == dir:     # �A�|�W�V�����Ɣ��������������ꍇ
            if( self.trade_pos.amount + amount ) <= AMOUNT_MAX:
                self.trade_pos.average_cost = ( self.trade_pos.average_cost * self.trade_pos.amount + rate * amount )/(self.trade_pos.amount + amount) # �擾���ω��i�X�V
                self.trade_pos.amount += amount     # �ۗL�����X�V
        elif self.trade_pos.dir != dir:     # �B�|�W�V�����Ɣ����������قȂ�ꍇ
            if self.trade_pos.amount >= amount: # (�ۗL���� �� ��������)�̏ꍇ
                self.update_profit(dir, rate, amount)    # �ꕔ���m
                self.trade_pos.amount -= amount           # �ۗL�����X�V
            elif self.trade_pos.amount < amount:  # (�ۗL���� < ��������)�̏ꍇ
                self.update_profit(dir, rate, self.trade_pos.amount)        # �S���m
                self.trade_pos.amount = amount - self.trade_pos.amount      # �ۗL�����X�V
                self.trade_pos.average_cost = rate                          # �擾���ω��i�X�V
                self.trade_pos.dir = dir                                    # �����X�V
    # ���v�X�V
    def update_profit(self, dir, rate, amount):
        self.profit_pre = self.profit
        if dir == "SELL":  # ���蒍���̏ꍇ
            self.profit += (rate - self.trade_pos.average_cost) * amount
        elif dir == "BUY":   # ���������̏ꍇ
            self.profit -= (rate - self.trade_pos.average_cost) * amount
    # �܂ݑ��v�v�Z
    def calc_inprofit(self, rate):
        self.inprofit_pre = self.inprofit
        if self.trade_pos.dir == "SELL": # ����|�W�̏ꍇ
            self.inprofit = (rate - self.trade_pos.average_cost) * self.trade_pos.amount
        elif self.trade_pos.dir == "BUY":  # �����|�W�̏ꍇ
            self.inprofit = (rate - self.trade_pos.average_cost) * self.trade_pos.amount



class trade(gym.Env):
    def __init__(self):
        super().__init__()
        # action_space, observation_space, reward_range ��ݒ肷��
        self.action_space = gym.spaces.Discrete(3)  # �g���[�_�[�̍s���̑I������
        self.observation_space = gym.spaces.Box(    
            low = 0.,          # �ŏ��l
            high = 10000.,     # �ő�l
            shape=(5,)         # �ϑ��l
        )
        self.reward_range = [-500000., 500000.] # WIN or LOSE
        self.trade_sys = trade_system()
        self._reset()

    def _reset(self):
        # ���X�̕ϐ�������������
        self.done = False
        self.trade_sys = trade_system()
        return self._observe()

    def _step(self, action):
        # 1�X�e�b�v�i�߂鏈�����L�q�B�߂�l�� observation, reward, done(�Q�[���I��������), info(�ǉ��̏��̎���)
        # �@���[�g�擾
        rate = self.trade_sys.tick_now["rate_ed"]
        # �A�g���[�h�A�N�V�������s( buy, sell, stay )
        if action == 0:
            self.trade_sys.order("BUY", rate, amount=AMOUNT_MAX)
        elif action == 1:
            self.trade_sys.order("SELL", rate, amount=AMOUNT_MAX)
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
        outfile.write( str(self.trade_sys.tick_now["rate_ed"])+"\t"+str(self.trade_sys.profit)+",\t"+str(self.trade_sys.inprofit)+'\n')
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
        rate_st = self.trade_sys.tick_now["rate_st"]
        rate_hi = self.trade_sys.tick_now["rate_hi"]
        rate_lo = self.trade_sys.tick_now["rate_lo"]
        rate_ed = self.trade_sys.tick_now["rate_ed"]
        production = self.trade_sys.tick_now["production"]
        observation = np.array([rate_st, rate_hi, rate_lo, rate_ed, production])
        return observation

    def _is_done(self):
         if self.trade_sys.now == (len(self.trade_sys.hist_data.index) - 1) :
             return True
         else:
             return False
