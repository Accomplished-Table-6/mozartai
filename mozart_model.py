import tensorflow as tf

def leaky_relu(features,alpha=0.2,name=None):
    return tf.maximum(alpha*features,features)

def default_model_params(img_height,vocabulary_size):
    params = dict()
    params["img_height"] = img_height
    params["img_width"] = None
    params["batch_size"] = 16
    params["img_channels"] = 1
    params["conv_blocks"] = 4
    params["conv_filter_n"] = [32,64,128,256]
    params["conv_filter_size"] = [[3,3],[3,3],[3,3],[3,3]]
    params["conv_pooling_size"] = [[2,2],[2,2],[2,2],[2,2]]
    params["rnn_units"] = 512
    params["rnn_layers"] = 2
    params["vocabulary_size"] = vocabulary_size
    return params

def ctc_cnn(params):
    # Input layer
    input = tf.keras.Input(shape=(params["img_height"],params["img_width"],params["img_channels"]),name="model_input")
    width_reduction = 1
    height_reduction = 1
    # Convolutional blocks
    x = input
    for i in range(params["conv_blocks"]):
        x = tf.keras.layers.Conv2D(filters=params["conv_filter_n"][i],kernel_size=params["conv_filter_size"][i],padding="same",activation=None)
        x = tf.keras.layers.BatchNormalization(x)
        x = leaky_relu(x)
        x = tf.keras.layers.MaxPooling2D(inputs=x,pool_size=params["conv_pooling_size"][i],strides=params["conv_pooling_size"][i])
        width_reduction = width_reduction*params["conv_pooling_size"][i][1]
        height_reduction = height_reduction*params["conv_pooling_size"][i][0]
    
    # Prepare output of conv block for recurrent blocks
    features = tf.transpose(x,perm=[2,0,3,1])
    feature_dim = params["conv_filter_n"][-1]*(params["img_height"]/height_reduction)
    feature_width = tf.shape(input)[2]/width_reduction
    features = tf.reshape(features,tf.stack([tf.cast(feature_width,"int32"),tf.shape(input)[0],tf.cast(feature_dim,"int32")]))
    # Recurrent block
    rnn_keep_prob = tf.keras.Input(shape=(),dtype=tf.float32,name="keep_prob")
    rnn_hidden_units = params["rnn_units"]
    rnn_hidden_layers = params["rnn_layers"]
    rnn_cells = [tf.keras.layers.LSTMCell(rnn_hidden_units) for _ in range(rnn_hidden_layers)]
    rnn_layer = tf.keras.layers.RNN(rnn_cells,return_sequences=True)(features)
    logits = tf.keras.layers.Dense(params["vocabulary_size"]+1,activation=None)(rnn_layer)
    # CTC Loss computation
    seq_len = tf.keras.Input(shape=None,dtype=tf.int32,name="seq_lengths")
    targets = tf.keras.Input(shape=None,dtype=tf.int32,name="target")
    ctc_loss = tf.nn.ctc_loss(labels=targets,inputs=logits,sequence_length=seq_len)
    loss = tf.reduce_mean(ctc_loss)
    # CTC decoding 
    decoded, log_prob = tf.nn.ctc_greedy_decoder(logits,seq_len)
    return input,seq_len,targets,decoded,loss,rnn_keep_prob
