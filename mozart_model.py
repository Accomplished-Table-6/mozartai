import tensorflow as tf

def leaky_relu(features, alpha=0.2, name=None):
    return tf.maximum(alpha * features, features)

def default_model_params(img_height, vocabulary_size):
    params = dict()
    params["img_height"] = img_height
    params["img_width"] = None
    params["batch_size"] = 1  # Processing measures sequentially
    params["img_channels"] = 1
    params["conv_blocks"] = 4
    params["conv_filter_n"] = [32, 64, 128, 256]
    params["conv_filter_size"] = [[3, 3], [3, 3], [3, 3], [3, 3]]
    params["conv_pooling_size"] = [[2, 2], [2, 2], [2, 2], [2, 2]]
    params["rnn_units"] = 512
    params["rnn_layers"] = 2
    params["vocabulary_size"] = vocabulary_size
    return params

class CTC_CNN_Model(tf.keras.Model):
    def __init__(self, params):
        super(CTC_CNN_Model, self).__init__()
        
        self.conv_layers = []
        for i in range(params["conv_blocks"]):
            self.conv_layers.append(tf.keras.layers.Conv2D(
                filters=params["conv_filter_n"][i],
                kernel_size=params["conv_filter_size"][i],
                padding="same",
                activation=None
            ))
            self.conv_layers.append(tf.keras.layers.BatchNormalization())
            self.conv_layers.append(tf.keras.layers.LeakyReLU(alpha=0.2))
            self.conv_layers.append(tf.keras.layers.MaxPooling2D(pool_size=params["conv_pooling_size"][i]))

        self.flatten = tf.keras.layers.Reshape((-1, params["conv_filter_n"][-1]))
        
        # **Stateful RNN Layer**
        self.rnn_layers = []
        for _ in range(params["rnn_layers"]):
            self.rnn_layers.append(tf.keras.layers.LSTM(
                params["rnn_units"], 
                return_sequences=True, 
                stateful=True  # 👈 Keeps memory across measures!
            ))

        self.dense = tf.keras.layers.Dense(params["vocabulary_size"] + 1, activation=None)
    
    def call(self, inputs):
        x = inputs
        for layer in self.conv_layers:
            x = layer(x)

        x = self.flatten(x)

        for rnn in self.rnn_layers:
            x = rnn(x)  # Stateful LSTM processing

        logits = self.dense(x)
        return logits
    
    def reset_states(self):
        """ Reset memory between different sheet music pieces. """
        for rnn in self.rnn_layers:
            rnn.reset_states()
