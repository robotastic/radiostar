#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time
from azure_software_radio import blob_sink


class fmrx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet")
        self.log = gr.logger("log_debug")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 240000

        ##################################################
        # Blocks
        ##################################################
        self.rtlsdr_source_0 = osmosdr.source("rtl=200")
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(88500000, 0)
        self.rtlsdr_source_0.set_gain(30, 0)
        self.rtlsdr_source_0.set_bandwidth(200000, 0)

        self.blocks_wavfile_sink_0 = blocks.wavfile_sink('/app/test.wav', 1, 48000, blocks.FORMAT_WAV, blocks.FORMAT_PCM_16)
        
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(1)
        
        self.analog_fm_demod_cf_0 = analog.fm_demod_cf(
        	channel_rate=240000,
        	audio_decim=5,
        	deviation=75000,
        	audio_pass=16000,
        	audio_stop=20000,
        	gain=1.0,
        	tau=75e-6,
        )
        
        self.blob_sink = blob_sink(
            authentication_method="url_with_sas",
            url="SAS URL goes here!",
            blob_name="radiostar-sdr",
            container_name="radiostar"
        )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.rtlsdr_source_0, 0), (self.analog_fm_demod_cf_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.blob_sink, 0))
        self.connect((self.analog_fm_demod_cf_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_wavfile_sink_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def closeEvent(self, event):
        self.log.debug("closeEvent()")
        event.accept()


def main(top_block_cls=fmrx, options=None):
    tb = top_block_cls()
    log = gr.logger("log_debug")    
    tb.start()

    time.sleep(10)

    tb.stop()

    tb.wait()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
