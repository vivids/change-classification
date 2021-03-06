'''
Created on Oct 8, 2018

@author: deeplearning
'''
import tensorflow as tf
import os
import constants as ct
import cv2
def parse_examples(serialized_example):
    features = tf.parse_single_example(serialized_example, features={
                        'label':tf.FixedLenFeature([], tf.string),
                        'curr_img':tf.FixedLenFeature([],tf.string),
                        'hist_img':tf.FixedLenFeature([],tf.string)})
    curr_img = tf.decode_raw(features['curr_img'],tf.uint8)
    hist_img = tf.decode_raw(features['hist_img'],tf.uint8)
    labels = tf.decode_raw(features['label'],tf.float32)
    curr_img=tf.reshape(curr_img,[ct.INPUT_SIZE,ct.INPUT_SIZE,ct.IMAGE_CHANNEL])
    hist_img = tf.reshape(hist_img,[ct.INPUT_SIZE,ct.INPUT_SIZE,ct.IMAGE_CHANNEL])
    labels = tf.reshape(labels, [ct.CLASS_NUM])
    return curr_img,hist_img,labels

# def conbineCurrAndHist2channelImage(curr_img,hist_img):
#     return tf.concat([curr_img,hist_img],2) 
    
def combine_image_batch(curr_img,hist_img,label):
    capacity = ct.MIN_AFTER_DEQUEUE+3*ct.BATCH_SIZE
    curr_img_batch,hist_img_batch,label_batch = tf.train.shuffle_batch([curr_img,hist_img,label],
                                                     batch_size=ct.BATCH_SIZE,capacity=capacity,
                                                     min_after_dequeue=ct.MIN_AFTER_DEQUEUE)
    return curr_img_batch,hist_img_batch,label_batch
 
def image_standardization(img):
    img = tf.cast(img, tf.float32)
    img = img/255.0
    return img
#     return tf.image.per_image_standardization(img)
        

def readImageFromTFRecord(category,shuffle =False,num_epochs=None,tfrecord_dir=ct.OUTPUT_TFRECORD_DIR):
    image_tfrecords = tf.train.match_filenames_once(os.path.join(tfrecord_dir,'data.'+category+'.tfrecord*'))
    image_reader = tf.TFRecordReader()
    image_queue = tf.train.string_input_producer(image_tfrecords,shuffle =shuffle,num_epochs=num_epochs)
    _,serialized_example = image_reader.read(image_queue)
    curr_img,hist_img,labels=parse_examples(serialized_example) 
    
    curr_img = image_standardization(curr_img)    
    hist_img = image_standardization(hist_img) 
#     image = conbineCurrAndHist2channelImage(curr_img,hist_img)
    return curr_img,hist_img,labels
    


def readImageBatchFromTFRecord(category):
    curr_img,hist_img,labels=readImageFromTFRecord(category,shuffle =True,num_epochs=None)
    curr_img_batch,hist_img_batch,label_batch = combine_image_batch(curr_img,hist_img,labels)
    return curr_img_batch,hist_img_batch,label_batch

