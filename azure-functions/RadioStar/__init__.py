import logging
import sys
sys.path.insert(0,'/usr/local/lib/python3/dist-packages')
sys.path.insert(0,'/usr/lib/python3/dist-packages')
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes

import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import time
from azure_software_radio import blob_source
import azure.functions as func


class fmrx(gr.top_block):

    def __init__(self, src_blob_name):
        gr.top_block.__init__(self, "Not titled yet")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 240000

        ##################################################
        # Blocks
        ##################################################
        src_blob_name = src_blob_name.split("/")

        self.blocks_wavfile_sink_0 = blocks.wavfile_sink("test.wav", 1, 48000, blocks.FORMAT_WAV, blocks.FORMAT_PCM_16)
        
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
        
        self.blob_source = blob_source(
            authentication_method="connection_string",
            connection_str=os.environ['AzureWebJobsStorage'],
            blob_name=src_blob_name[1],
            container_name=src_blob_name[0]
        )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blob_source, 0), (self.analog_fm_demod_cf_0, 0))
        self.connect((self.analog_fm_demod_cf_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_wavfile_sink_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def closeEvent(self, event):
        event.accept()


def main(myblob: func.InputStream):
    tb = fmrx(myblob.name)  
    tb.start()

    tb.wait()
    
    logging.info(myblob.name)
    logging.info(myblob)
