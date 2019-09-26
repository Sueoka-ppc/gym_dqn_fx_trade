# coding: utf-8
import sys

import pandas as pd
import numpy as np
import queue
import csv

from  .Technical_Indicators import mv_avrg, rsi, ichimoku, DeviationRate

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

        # �`���[�g��ǂݍ���
        self.cols = ["YMD", "HM", "open", "high", "low", "close", "volume"]
        self.chart = pd.read_csv(PATH, names=self.cols )
        self.tick_num = 0
        self.tick = self.chart.iloc[self.tick_num]
        
        # �C���W�P�[�^���쐬
        # �@25���ړ����ϐ�������
        df = mv_avrg(self.chart.close, window_size=25)
        self.chart['mv_avrg_div'] = DeviationRate(self.chart.close, df)
        
        # �A14��RSI
        self.chart['RSI'] = rsi(self.chart.close, window_size=14)/100
        
        # �B��ڋύt�\������
        df = ichimoku(self.chart)
        self.chart['tenkan_div'] = DeviationRate(self.chart.close, df.tenkan)
        self.chart['base'] = DeviationRate(self.chart.close, df.base)
        self.chart['senkou1'] = DeviationRate(self.chart.close, df.senkou1)
        self.chart['senkou2'] = DeviationRate(self.chart.close, df.senkou2)
        
        # N�{��tick��i�߂�
        N = 100
        self.tick_num = N
        self.tick = self.chart.iloc[N]
        
        self.reset()

    def reset(self):
        self.tick = self.chart.iloc[0]
        self.tick_num = 0
        self.profit     = 0             # ���v
        self.inprofit   = 0             # �܂ݑ��v
        self.trade_pos  = trade_pos()   # �|�W�V����

    # Tick�X�V
    def update_tick(self):
        self.tick_num += 1
        if self.tick_num < len(self.chart.index):
            self.tick = self.chart.iloc[self.tick_num]
        self.calc_inprofit(self.tick.close)
                

    # ����(��/��, ���[�g, ��)
    def order(self, dir, rate, amount):
        # dir ; ����["BUY", "SELL"]
        # rate  : �������i
        # amount: ��������

        # �X�v���b�h�ŕ␳
        if dir == "BUY":
            rate += self.spread
        elif dir == "SELL":
            rate -= self.spread

        # �������� �~ ���o���b�W
        amount = amount * 10000 * self.leverage

        # ����(���)
         # �@�V�K����/�V�K����
        if self.trade_pos.amount == 0:
            self.trade_pos.average_cost = rate  # �擾���ω��i = �������i
            self.trade_pos.amount = amount      # �ۗL����     = ��������
            self.trade_pos.dir = dir
         # �A��������/���葝��
        elif self.trade_pos.dir == dir:
            if( self.trade_pos.amount + amount ) <= AMOUNT_MAX:
                self.trade_pos.average_cost = ( self.trade_pos.average_cost * self.trade_pos.amount + rate * amount )/(self.trade_pos.amount + amount) # �擾���ω��i�X�V
                self.trade_pos.amount += amount     # �ۗL�����X�V
        # �B���Δ���
        elif self.trade_pos.dir != dir:
            # �ꕔ����
            if self.trade_pos.amount >= amount:                             # (�ۗL���� �� ��������)�̏ꍇ
                self.update_profit(rate, amount)                            # �ꕔ���m/�ꕔ����
                self.trade_pos.amount -= amount                             # �ۗL�����X�V
            # �h�e������/�h�e������
            elif self.trade_pos.amount < amount:                            # (�ۗL���� < ��������)�̏ꍇ
                self.update_profit(rate, self.trade_pos.amount)             # �S���m/�S���� (+ �V�K����/�V�K����)
                self.trade_pos.amount = amount - self.trade_pos.amount      # �ۗL�����X�V
                self.trade_pos.average_cost = rate                          # �擾���ω��i�X�V
                self.trade_pos.dir = dir                                    # ���΃|�W�V����

        if self.trade_pos.amount == 0:
            self.trade_pos.dir ="NANE"

    # ���v�X�V
    def update_profit(self, rate, amount):
        if self.trade_pos.dir == "BUY":  # ���|�W�̏ꍇ
            self.profit += (rate - self.trade_pos.average_cost) * amount
        elif self.trade_pos.dir == "SELL":   # ���|�W�̏ꍇ
            self.profit -= (rate - self.trade_pos.average_cost) * amount

    # �܂ݑ��v�v�Z
    def calc_inprofit(self, rate):
        if self.trade_pos.dir == "SELL": # ����|�W�̏ꍇ
            self.inprofit =-(rate - self.trade_pos.average_cost) * self.trade_pos.amount
        elif self.trade_pos.dir == "BUY":  # �����|�W�̏ꍇ
            self.inprofit = (rate - self.trade_pos.average_cost) * self.trade_pos.amount
        else:
            self.inprofit = 0


if __name__ == "__main__":
    TS = trade_system()
    print(TS.chart[100:].head(5))
