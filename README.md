# MozartAI
This is a CRNN network based on this github project: https://github.com/OMR-Research/tf-end-to-end and the accompanying paper and dataset here: https://grfia.dlsi.ua.es/primus/
## Purpose
The purpose of this CRNN is to recognize music. However, I wish to package it in a friendly way so that it can be used by people who have little to no coding experience. 
## Components
Most of the model has been built on the githib project but with updated code as the original used functions based on Tensorflow V1. 
Furthermore, the semantic output was a space seperated string which was quite annoying to parse and is not the final intended output anyway.
This has instead been replaced by a list. 
The program xmlencoder.py was added to allow the easy conversion of the output to a musicxml file readable format.
The final program will include two trained models which are each suited to different image qualities. One will be trained on Camera-PrIMuS and the other will be trained on the regular PrIMuS datset.


