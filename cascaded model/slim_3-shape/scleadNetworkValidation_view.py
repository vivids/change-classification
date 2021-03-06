'''
Created on Oct 10, 2018

@author: deeplearning
'''

import tensorflow as tf
import constants as ct
from scleadNetworkArchitecture import foward_propagation
from readImageFromTFRecord import readImageFromTFRecord
from loadImageAndConvertToTFRecord import loadImageAndConvertToTFRecord, isFileExist
from writeAndReadFiles import readInfoFromFile
import time
import cv2
import os
import numpy as np

def validate_network():
    if not ct.VALIDATION_PERCENTAGE:
        loadImageAndConvertToTFRecord(test_percentage=0,validation_percentage=100,inputDataDir=ct.TEST_DATASET_PATH,
                                      infoSavePath=ct.TEST_INFOMATION_PATH,tfrecordPath=ct.TEST_TFRECORD_DIR)
        dataSetSizeList = readInfoFromFile(ct.TEST_INFOMATION_PATH)
    else:
        dataSetSizeList = readInfoFromFile(ct.INFORMATION_PATH)
#     dataSetSizeList = readInfoFromFile(ct.INFORMATION_PATH)
    validation_image_num = int(dataSetSizeList['validation'])
    image_inputs=tf.placeholder(tf.float32, (1,ct.INPUT_SIZE,ct.INPUT_SIZE,ct.IMAGE_CHANNEL*2), 'validation_inputs')
    label_inputs =tf.placeholder(tf.float32,(1,ct.CLASS_NUM), 'validation_outputs')

    nn_output,layer_outputs_tensor = foward_propagation(image_inputs,is_training=False)
    label_value_tensor = tf.argmax(label_inputs,1)
    pred_value_tensor = tf.argmax(nn_output,1)
#     correct_prediction = tf.equal(tf.argmax(nn_output,1), tf.argmax(label_inputs,1))
#     accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))
   
    image_tensor,label_tensor= readImageFromTFRecord(ct.CATELOGS[2],tfrecord_dir= ct.TEST_TFRECORD_DIR)
    saver = tf.train.Saver()
    with tf.Session() as sess :
         
        tf.local_variables_initializer().run()
        tf.global_variables_initializer().run()
        
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess, coord=coord)
        while(True):
#             TP = 0
#             FN = 0
#             FP = 0
#             TN = 0
#             sample_num = [0 for _ in range(7)]
#             correct_num = [0 for _ in range(7)]
            ckpt = tf.train.get_checkpoint_state(ct.MODEL_SAVE_PATH)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess,ckpt.model_checkpoint_path)
                global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
                for i in range(validation_image_num):
                    test_image, test_label = sess.run([image_tensor,label_tensor])
                    pred,label,layer_outputs = sess.run([pred_value_tensor,label_value_tensor,layer_outputs_tensor], feed_dict= {image_inputs:[test_image],label_inputs:[test_label]})
                    
                    feature_map_path=os.path.join(ct.FEATURE_MAP,str(i))
                    isFileExist(feature_map_path)
                    feature_map = layer_outputs['resnet_v2_50/block3/unit2/bottleneck_v2']
                    predict = layer_outputs['prediction']
                    with open(os.path.join(feature_map_path,'predict'),'w') as f:
                            f.write(str(predict))
                            f.write('\n')

                    feature_map = np.squeeze(feature_map)
                    feature_map = cv2.split(feature_map)
#                     cv2.namedWindow('3',0)
                    for i in range(len(feature_map)): 
                            cv2.imwrite(os.path.join(feature_map_path,str(i)+'.jpg'),feature_map[i]*255)
#                         cv2.imshow('3',feature_map[i])
#                         cv2.waitKey()
#                     pred,label = sess.run([pred_value_tensor,label_value_tensor], feed_dict= {image_inputs:[test_image],label_inputs:[test_label]})
#                     if label[0]:
#                         if pred[0]:
#                             TP+=1
#                         else:
#                             FN+=1
#                     else:
#                         if not pred[0]:
#                             TN+=1
#                         else:
#                             FP+=1
#                     index = label[0]
#                     sample_num[index]+=1
#                     if pred[0] == index:
#                         correct_num[index]+=1

#                 print(sample_num)
#                 print(positive_sample_num)
#                 print(negative_sample_num)       
#                 accuracy = (TP+TN)/(TP+FN+TN+FP)
#                 precision = TP/(TP+FP+1e-8)
#                 recall = TP/(TP+FN)
#                 f1 = 2*precision*recall/(precision+recall+1e-8)
#                 correct_num = sum(correct_num)
#                 accuracy_score = correct_num / sum(sample_num)
#                 print('after %s iteration, the validation accuracy is %g'%(global_step,accuracy_score))
#                 print('after %s iteration, the  accuracy is %g,precision is %g,recall is %g,F1 is %g'%(global_step,accuracy,precision,recall,f1))
            else:
                print('no model')
#             update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
#             print(sess.run(update_ops))
            if int(global_step)>ct.STEPS:
                break 
            print('running..........')
            time.sleep(100)
        coord.request_stop()
        coord.join(threads) 
                           
if __name__ == '__main__':
#     for i in range(545):
#         print('after %d min, the validation will be start'%(545-i))
#         time.sleep(60)
        
    with tf.device('/cpu:0'):            
        validate_network()      
                                                              
