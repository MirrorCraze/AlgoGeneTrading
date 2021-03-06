# -*- coding: utf-8 -*-
"""MACD EMA 12v26 with trailing stoploss.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14gZSXyekCtFX9PnVd0qv7AyqPvFZtwPW
"""

from AlgoAPI import AlgoAPIUtil, AlgoAPI_Backtest
from datetime import datetime, timedelta
import talib, numpy

class AlgoEvent:
    def __init__(self): ###like a constructor, so all member variables are accessible throughout lifetime of AlgoEvent Object
        self.lasttradetime = datetime(2000,1,1)
        self.lastTradeTime = {}
        self.dictClose = {}
        self.dictWeekMA = {}
        self.dictDayMA = {}
        self.dictMACD = {}
        self.dictHisMACD = {}
        self.weekPeriod = 13
        self.dayPeriod = 6
        self.stickAmount = 2 #10 candlesticks
        self.loop = 0
        self.buy = 0
        self.sell = 0
        self.stopPercent = 0.02
        ########################################
        self.dictLogReturn = {} #PAT
        ########################################

    def start(self, mEvt): ###declare assets
        self.myinstrument = mEvt['subscribeList'] #In case of subscribing to multiple CFDs
        for instru in self.myinstrument:
            self.dictClose[instru] = numpy.array([])
            self.lastTradeTime[instru] = datetime(2000,1,1)
            self.dictWeekMA[instru] = numpy.array([])
            self.dictDayMA[instru] = numpy.array([])

            ###################################################
            self.dictLogReturn[instru]=numpy.array([]) #PAT
            ###################################################

        self.evt = AlgoAPI_Backtest.AlgoEvtHandler(self, mEvt)
        self.evt.start()

    def on_bulkdatafeed(self, isSync, bd, ab):
        for instru in self.myinstrument:
            #if bd[instru]['timestamp'] >= self.lasttradetime + timedelta(hours=24) :
            if True:
                self.dictClose[instru] = numpy.append(self.dictClose[instru], bd[instru]['lastPrice']) ###same

                self.lasttradetime = bd[instru]['timestamp']
                lastprice = bd[instru]['lastPrice']
                self.lastTradeTime[instru]= bd[instru]['timestamp']
                #self.dictClose[instru] = numpy.append(self.dictClose[instru],lastprice) ###same
                ########################################################################################
                #PAT Calculate log return
                if len(self.dictClose[instru]) > 1:
                    logReturn=numpy.log(self.dictClose[instru][-1]/self.dictClose[instru][-2])
                    self.dictLogReturn[instru]=numpy.append(self.dictLogReturn[instru],logReturn)
                    #self.evt.consoleLog("dictLogReturn ",self.dictLogReturn[instru])
                ########################################################################################
                
                fastPer = self.stickAmount * self.dayPeriod
                slowPer = self.stickAmount * self.weekPeriod
                
                # keep the most recent observations 
                if len(self.dictClose[instru]) > int(fastPer+slowPer):
                    self.dictClose[instru] = self.dictClose[instru][-int(self.weekPeriod + self.dayPeriod)*self.stickAmount:] ###omit the first element WHY???
                    #self.evt.consoleLog("dictClose recent ",self.dictClose[instru]) ###debug

                # fit SMA line
                self.dictWeekMA[instru] = talib.EMA(self.dictClose[instru], timeperiod=int(slowPer))
                self.dictDayMA[instru] = talib.EMA(self.dictClose[instru], timeperiod=int(fastPer))
                if not (numpy.isnan(self.dictWeekMA[instru][-1]) or numpy.isnan(self.dictWeekMA[instru][-2]) or numpy.isnan(self.dictDayMA[instru][-1]) or numpy.isnan(self.dictDayMA[instru][-2])):
                    
                    ##########################################################################
                    #PAT Calculate SD of log return
                    if len(self.dictLogReturn[instru]) < self.stickAmount:
                        sd = numpy.std(self.dictLogReturn[instru])
                        #self.evt.consoleLog("std(<10elements) ", sd)
                    else:
                        sd=numpy.std(self.dictLogReturn[instru][-self.stickAmount:])
                        #self.evt.consoleLog("std ", sd)
                    ##########################################################################
                    
                    #calculate MACD = dayMA (fastMA) - WeekMA (slowMA)
                    self.dictMACD[instru],signal,self.dictHisMACD[instru] = talib.MACD(self.dictClose[instru],fastperiod = fastPer,slowperiod = slowPer, signalperiod = 9)
                    if((self.dictHisMACD[instru][-1] > 0 and self.dictHisMACD[instru][-2] < 0)or (self.dictHisMACD[instru][-1] > self.dictHisMACD[instru][-2] and self.dictHisMACD[instru][-2] > 0)):
                        self.test_sendOrderNoShort(lastprice,1,'open',instru,sd)
                    elif ((self.dictHisMACD[instru][-1] < 0 and self.dictHisMACD[instru][-2] > 0)or (self.dictHisMACD[instru][-1] < self.dictHisMACD[instru][-2] and self.dictHisMACD[instru][-2] < 0)):
                        self.test_sendOrderNoShort(lastprice,-1,'open',instru,sd)
                    
                    
                    
                    #bullish trade : weekly SMA positive, daily SMA negative => buy stop order on swing high above daily SMA
                    #if (self.dictWeekMA[instru][-1] > self.dictWeekMA[instru][-2] and self.dictDayMA[instru][-1] < self.dictDayMA[instru][-2] and self.dictClose[instru][-1] <self.dictDayMA[instru][-1]):
                     #       self.test_sendOrder(lastprice,1,'open',instru,sd)
                    #bearish trade : weekly SMA negative, daily SMA positive => sell stop order on swing slow below daily SMA
                    #if (self.dictWeekMA[instru][-1] < self.dictWeekMA[instru][-2] and self.dictDayMA[instru][-1] > self.dictDayMA[instru][-2] and self.dictClose[instru][-1] > self.dictDayMA[instru][-1]):
                     #       self.test_sendOrder(lastprice,-1,'open',instru,sd)
    
                        
    
    def on_marketdatafeed(self, md, ab):
        pass

    def on_orderfeed(self, of):
        pass

    def on_dailyPLfeed(self, pl):
        pass

    def on_openPositionfeed(self, op, oo, uo):
        pass
        curOO = oo.copy()
        self.evt.consoleLog("LOOP" + str(self.loop))
        self.loop +=1
        for tradeID in curOO:
            instrument = oo[tradeID]['instrument']
            self.evt.consoleLog("TIME for" + str(tradeID) + "IS" + str(oo[tradeID]['opentime']))
            self.evt.consoleLog("TIME for last" + str(instrument) + "IS" + str(self.lastTradeTime[instrument] + timedelta(days=1, hours = 12)))
            if oo[tradeID]['opentime'] < self.lastTradeTime[instrument]:
                self.evt.consoleLog("Break with" + str(tradeID))
                break
            else:
                self.evt.consoleLog("Continue with " + str(tradeID))
            buysell = oo[tradeID]['buysell']
            openprice = oo[tradeID]['openprice']
            Volume = oo[tradeID]['Volume']
            profitLev = oo[tradeID]['takeProfitLevel']
            stopLossLev = oo[tradeID]['stopLossLevel']
            sd=numpy.std(self.dictLogReturn[instrument][-self.stickAmount:])
            #self.evt.consoleLog("Last price at " + str(self.lastTradeTime) + " for " + str(instrument) + " is " + str(self.dictClose[instrument][-1]))
            if buysell == 1 and openprice < self.dictClose[instrument][-1]:
                oo[tradeID]['openprice'] = self.dictClose[instrument][-1]
                #self.evt.consoleLog("Change openprice to " + str(self.dictClose[instrument][-1]))
                openprice = oo[tradeID]['openprice']
                oo[tradeID]['stopLossLevel'] = openprice *(1-(sd+0.02))
                oo[tradeID]['takeProfitLevel'] = openprice * (1.1)
            elif buysell == -1 and openprice > self.dictClose[instrument][-1]:
                oo[tradeID]['openprice'] = self.dictClose[instrument][-1]
                #self.evt.consoleLog("Change openprice to " + str(self.dictClose[instrument][-1]))
                openprice = oo[tradeID]['openprice']
                oo[tradeID]['stopLossLevel'] = openprice *(1.1)
                oo[tradeID]['takeProfitLevel'] = openprice * (1-(sd+0.02))
            
                #self.evt.consoleLog("Change openprice to " + str(self.dictClose[instrument][-1]))
            #elif buysell == -1 and openprice > self.dictClose[instrument][-1]:
                #oo[tradeID]['openprice'] = self.dictClose[instrument][-1]
                #self.evt.consoleLog("Change openprice to " + str(self.dictClose[instrument][-1]))
                #openprice = oo[tradeID]['openprice']
                #oo[tradeID]['stopLossLevel'] = openprice *1.1
                #oo[tradeID]['takeProfitLevel'] = openprice * 0.9
            

    def test_sendOrder(self, lastprice, buysell, openclose,instru,sd):
        self.evt.consoleLog(instru, " : ", lastprice)
        if buysell == 1:
            self.evt.consoleLog("buy")
        else:
            self.evt.consoleLog("sell")
        orderObj = AlgoAPIUtil.OrderObject()
        orderObj.instrument = instru
        orderObj.orderRef = 1
        if buysell==1:
            orderObj.takeProfitLevel = lastprice*1.1
            orderObj.stopLossLevel = lastprice*0.9 #PAT
        elif buysell==-1:
            orderObj.takeProfitLevel = lastprice*0.9
            orderObj.stopLossLevel = lastprice*1.1 #PAT
        self.evt.consoleLog("stoploss ",orderObj.stopLossLevel) #PAT
        orderObj.volume = 0.01
        orderObj.openclose = openclose
        orderObj.buysell = buysell
        orderObj.ordertype = 0 #0=market_order, 1=limit_order
        self.evt.sendOrder(orderObj)
    def test_sendOrderNoShort(self, lastprice, buysell, openclose,instru,sd):
        self.evt.consoleLog(instru, " : ", lastprice)
        if buysell == 1:
            self.evt.consoleLog("buy")
        else:
            self.evt.consoleLog("sell")
        orderObj = AlgoAPIUtil.OrderObject()
        orderObj.instrument = instru
        orderObj.orderRef = 1
        self.evt.consoleLog("stoploss ",orderObj.stopLossLevel) #PAT
        orderObj.volume = 0.01
        orderObj.openclose = openclose
        orderObj.buysell = buysell
        orderObj.ordertype = 0 #0=market_order, 1=limit_order
        self.evt.sendOrder(orderObj)