# coding: utf-8
import sys

import pandas as pd
import numpy as np
import csv


PATH = './data/USDJPY1_20181016.csv'
AMOUNT_MAX = 1

class trade_pos():
    def __init__(self):
        self.dir = "NANE"
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

    # Tick�X�V
    def update_tick(self):
        self.now += 1
        if self.now < len(self.hist_data.index):
            self.tick_now = self.hist_data.iloc[self.now]
        else:
            self.now = 0

    # ����
    def order(self, dir, rate, amount):
        # dir ; ����["BUY", "SELL"]
        # rate  : �������i
        # amount: ��������

        # �X�v���b�h�l��
        if dir == "BUY":
            rate += self.spread
        elif dir == "SELL":
            rate -= self.spread

        # ���o���b�W
        amount = amount * 10000 * self.leverage

        # �I�[�_�[���s
         # �@�|�W�V���������̏ꍇ
        if self.trade_pos.amount == 0:
            self.trade_pos.average_cost = rate  # �擾���ω��i = �������i
            self.trade_pos.amount = amount      # �ۗL����     = ��������
            self.trade_pos.dir = dir
         # �A�|�W�V�����Ɣ��������������ꍇ
        elif self.trade_pos.dir == dir:
            if( self.trade_pos.amount + amount ) <= AMOUNT_MAX:
                self.trade_pos.average_cost = ( self.trade_pos.average_cost * self.trade_pos.amount + rate * amount )/(self.trade_pos.amount + amount) # �擾���ω��i�X�V
                self.trade_pos.amount += amount     # �ۗL�����X�V
         # �B�|�W�V�����Ɣ����������قȂ�ꍇ
        elif self.trade_pos.dir != dir:     
            if self.trade_pos.amount >= amount: # (�ۗL���� �� ��������)�̏ꍇ
                self.update_profit(rate, amount)    # �ꕔ���m
                self.trade_pos.amount -= amount           # �ۗL�����X�V
            elif self.trade_pos.amount < amount:  # (�ۗL���� < ��������)�̏ꍇ
                self.update_profit(rate, self.trade_pos.amount)             # �S���m
                self.trade_pos.amount = amount - self.trade_pos.amount      # �ۗL�����X�V
                self.trade_pos.average_cost = rate                          # �擾���ω��i�X�V
                self.trade_pos.dir = dir                                    # �����X�V

        if self.trade_pos.amount == 0:
            self.trade_pos.dir ="NANE"

    # ���v�X�V
    def update_profit(self, rate, amount):
        self.profit_pre = self.profit
        if self.trade_pos.dir == "BUY":  # ���|�W�̏ꍇ
            self.profit += (rate - self.trade_pos.average_cost) * amount
        elif self.trade_pos.dir == "SELL":   # ���|�W�̏ꍇ
            self.profit -= (rate - self.trade_pos.average_cost) * amount

    # �܂ݑ��v�v�Z
    def calc_inprofit(self, rate):
        self.inprofit_pre = self.inprofit
        if self.trade_pos.dir == "SELL": # ����|�W�̏ꍇ
            self.inprofit =-(rate - self.trade_pos.average_cost) * self.trade_pos.amount
        elif self.trade_pos.dir == "BUY":  # �����|�W�̏ꍇ
            self.inprofit = (rate - self.trade_pos.average_cost) * self.trade_pos.amount
        else:
            self.inprofit = 0



