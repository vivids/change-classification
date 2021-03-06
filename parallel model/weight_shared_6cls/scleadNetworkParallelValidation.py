'''
Created on Oct 10, 2018

@author: deeplearning
'''

import tensorflow as tf
import constants as ct
from scleadNetworkParallelArchitecture import forward_propagation
from readImageFromTFRecord import readImageFromTFRecord
from loadImageAndConvertToTFRecord import loadImageAndConvertToTFRecord, isFileExist
from writeAndReadFiles import readInfoFromFile
import time

def validate_network():
    if not ct.VALIDATION_PERCENTAGE:
        loadImageAndConvertToTFRecord(test_percentage=0,validation_percentage=100,inputDataDir=ct.TEST_DATASET_PATH,
                                      infoSavePath=ct.TEST_INFOMATION_PATH,tfrecordPath=ct.TEST_TFRECORD_DIR)
        dataSetSizeList = readInfoFromFile(ct.TEST_INFOMATION_PATH)
    else:
        dataSetSizeList = readInfoFromFile(ct.INFORMATION_PATH)
#     dataSetSizeList = readInfoFromFile(ct.INFORMATION_PATH)
    validation_image_num = int(dataSetSizeList['validation'])
#     image_inputs=tf.placeholder(tf.float32, (1,ct.INPUT_SIZE,ct.INPUT_SIZE,ct.IMAGE_CHANNEL*2), 'validation_inputs')
#     label_inputs =tf.placeholder(tf.float32,(1,ct.CLASS_NUM), 'validation_outputs')
    curr_image_inputs=tf.placeholder(tf.float32, (1,ct.INPUT_SIZE,ct.INPUT_SIZE,ct.IMAGE_CHANNEL), 'curr_inputs')
    hist_image_inputs=tf.placeholder(tf.float32, (1,ct.INPUT_SIZE,ct.INPUT_SIZE,ct.IMAGE_CHANNEL), 'hist_inputs')
    label_inputs =tf.placeholder(tf.float32,(1,ct.CLASS_NUM), 'outputs')
    
    nn_output,_ = forward_propagation(curr_image_inputs,hist_image_inputs,is_training=False)
    label_value_tensor = tf.argmax(label_inputs,1)
    pred_value_tensor = tf.argmax(nn_output,1)
#     correct_prediction = tf.equal(tf.argmax(nn_output,1), tf.argmax(label_inputs,1))
#     accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))
    
    curr_img_tensor,hist_img_tensor,label_tensor= readImageFromTFRecord(ct.CATELOGS[2],tfrecord_dir= ct.TEST_TFRECORD_DIR)
#     curr_img_tensor=tf.reshape(curr_img_tensor,[1,ct.INPUT_SIZE,ct.INPUT_SIZE,ct.IMAGE_CHANNEL])
#     hist_img_tensor = tf.reshape(hist_img_tensor,[1,ct.INPUT_SIZE,ct.INPUT_SIZE,ct.IMAGE_CHANNEL])
#     label_tensor = tf.reshape(label_tensor,[1,ct.CLASS_NUM])
    
    saver = tf.train.Saver()
    with tf.Session() as sess :
         
        tf.local_variables_initializer().run()
        tf.global_variables_initializer().run()
        
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess, coord=coord)
        while(True):
            sample_num = [0 for _ in range(7)]
            correct_num = [0 for _ in range(7)]
            inference_time=0
            ckpt = tf.train.get_checkpoint_state(ct.MODEL_SAVE_PATH)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess,ckpt.model_checkpoint_path)
                global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
                for _ in range(validation_image_num):
#                     start_time = time.time()
                    curr_img,hist_img,label = sess.run([curr_img_tensor,hist_img_tensor,label_tensor])
                    pred,label = sess.run([pred_value_tensor,label_value_tensor], feed_dict= {curr_image_inputs:[curr_img],hist_image_inputs:[hist_img],label_inputs:[label]})
#                     inference_time+=(time.time()-start_time)
                    index = label[0]
                    sample_num[index]+=1
                    if pred[0] == index:
                        correct_num[index]+=1

#                 print(sample_num)
#                 print(positive_sample_num)
#                 print(negative_sample_num)       
#                 accuracy = (TP+TN)/(TP+FN+TN+FP)
#                 precision = TP/(TP+FP+1e-8)
#                 recall = TP/(TP+FN)
#                 f1 = 2*precision*recall/(precision+recall+1e-8)
#                 print(inference_time/(TP+FN+TN+FP))
                accuracy_score = sum(correct_num) / sum(sample_num)
                proportion = [correct_num[i]/sample_num[i] for i in range(ct.CLASS_NUM)]
                print('after %s iteration, the validation accuracy is %g'%(global_step,accuracy_score))
                print('stain:%g, luminance:%g, rotation:%g, abnormal:%g, foreignBody:%g, character:%g'%(proportion[0],proportion[1],proportion[2],proportion[3],proportion[4],proportion[5]))               
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
#     for i in range(425):
#         print('after %d min, the training will be start'%(425-i))
#         time.sleep(60)
    with tf.device('/cpu:0'):            
        validate_network()     
                                                              
