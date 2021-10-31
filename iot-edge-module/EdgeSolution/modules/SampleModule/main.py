# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
import asyncio
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient

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
            self.freq = int(os.environ['APP_FREQ'])

                           
        print("rtl_src: {} ENV: {}".format(self.rtl_src,os.environ.get('APP_RTL_SRC') ))
        print("freq: {} ENV: {}".format(self.freq,os.environ.get('APP_FREQ')))
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


async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()

        # # define behavior for receiving an input message on input1
        # async def input1_listener(module_client):
        #     while True:
        #         input_message = await module_client.receive_message_on_input("input1")  # blocking call
        #         print("the data in the message received on input1 was ")
        #         print(input_message.data)
        #         print("custom properties are")
        #         print(input_message.custom_properties)
        #         print("forwarding mesage to output1")
        #         await module_client.send_message_to_output(input_message, "output1")

        # # define behavior for halting the application
        # def stdin_listener():
        #     while True:
        #         try:
        #             selection = input("Press Q to quit\n")
        #             if selection == "Q" or selection == "q":
        #                 print("Quitting...")
        #                 break
        #         except:
        #             time.sleep(10)

        # # Schedule task for C2D Listener
        # listeners = asyncio.gather(input1_listener(module_client))

        # print ( "The sample is now waiting for messages. ")

        # # Run the stdin listener in the event loop
        # loop = asyncio.get_event_loop()
        # user_finished = loop.run_in_executor(None, stdin_listener)

        # # Wait for user to indicate they are done listening for messages
        # await user_finished

        # Cancel listening
        #listeners.cancel()



        if os.environ.get('APP_REC_TIME')!=None:
            rec_time = int(os.environ['APP_REC_TIME'])
        else:
            rec_time = 60
        if os.environ.get('APP_REST_TIME')!=None:
            rest_time = int(os.environ['APP_REST_TIME'])
        else:
            rest_time = 600

        
        log = gr.logger("log_debug")    
        
        while True:
            tb = fmrx()
            tb.start()
            print("Recording for: {}".format(rec_time))
            time.sleep(rec_time)

            tb.stop()

            tb.wait()

            print("Resting for: {}".format(rest_time))
            time.sleep(rest_time)

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    print(os.environ.keys())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())