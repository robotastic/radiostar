#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion
import logging
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys, os
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time
from azure_software_radio import blob_sink
from datetime import datetime, timedelta

class fmrx(gr.top_block):



    def __init__(self):

        self.rtl_src = "rtl=200"
        self.freq = 88500000 
        self.connection_str = None

        #print(os.environ.keys())
        if os.environ.get('APP_RTL_SRC')!=None:
            self.rtl_src = os.environ['APP_RTL_SRC']
        
        if os.environ.get('APP_CONNECTION_STR')!=None:
            self.connection_str = os.environ['APP_CONNECTION_STR']
        else:
            print("APP_CONNECTION_STR env var needs to be defined")

        if os.environ.get('APP_FREQ')!=None:
            self.freq = os.environ['APP_FREQ']

                           

        gr.top_block.__init__(self, "Not titled yet")
        self.log = gr.logger("log_debug")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 240000

        ##################################################
        # Blocks
        ##################################################
        self.rtlsdr_source_0 = osmosdr.source(self.rtl_src)
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(self.freq, 0)
        self.rtlsdr_source_0.set_gain(30, 0)
        self.rtlsdr_source_0.set_bandwidth(200000, 0)

        #self.blocks_wavfile_sink_0 = blocks.wavfile_sink('/app/original.wav', 1, 48000, blocks.FORMAT_WAV, blocks.FORMAT_PCM_16)
        
        #self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(1)
        
        # self.analog_fm_demod_cf_0 = analog.fm_demod_cf(
        # 	channel_rate=240000,
        # 	audio_decim=5,
        # 	deviation=75000,
        # 	audio_pass=16000,
        # 	audio_stop=20000,
        # 	gain=1.0,
        # 	tau=75e-6,
        # )
        
        blob_name = "raw_{}_{}.iq".format(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'), self.freq)
        
        self.blob_sink = blob_sink(
            authentication_method="connection_string",
            connection_str=self.connection_str,
            blob_name=blob_name,
            container_name="inbox"
        )


        ##################################################
        # Connections
        ##################################################
        #self.connect((self.rtlsdr_source_0, 0), (self.analog_fm_demod_cf_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.blob_sink, 0))
        #self.connect((self.analog_fm_demod_cf_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        #self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_wavfile_sink_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def closeEvent(self, event):
        self.log.debug("closeEvent()")
        event.accept()


def main(top_block_cls=fmrx, options=None):
    if os.environ.get('APP_REC_TIME')!=None:
        rec_time = os.environ['APP_REC_TIME']
    else:
        rec_time = 60
    tb = top_block_cls()
    log = gr.logger("log_debug")    
    tb.start()

    time.sleep(rec_time)

    tb.stop()

    tb.wait()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
