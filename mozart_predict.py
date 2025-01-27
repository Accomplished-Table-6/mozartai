import argparse
import tensorflow as tf
import mozart_utils
import cv2
import numpy as np


# Parse arguments
parser = argparse.ArgumentParser(description='Decode a music score image with a trained model (CTC).')
parser.add_argument('-image', dest='image', type=str, required=True, help='Path to the input image.')
parser.add_argument('-model', dest='model', type=str, required=True, help='Path to the trained model.')
parser.add_argument('-vocabulary', dest='voc_file', type=str, required=True, help='Path to the vocabulary file.')
args = parser.parse_args()

# Debugging: Verify input paths
print(f"Image path: {args.image}")
print(f"Model path: {args.model}")
print(f"Vocabulary path: {args.voc_file}")

# Check TensorFlow compatibility
tf.compat.v1.reset_default_graph()
sess = tf.compat.v1.InteractiveSession()
tf.compat.v1.disable_eager_execution()

# Load vocabulary
try:
    with open(args.voc_file, 'r') as dict_file:
        dict_list = dict_file.read().splitlines()
        int2word = {idx: word for idx, word in enumerate(dict_list)}
    print(f"Loaded vocabulary with {len(int2word)} entries.")
except Exception as e:
    print(f"Error loading vocabulary: {e}")
    exit(1)

# Restore model
try:
    saver = tf.compat.v1.train.import_meta_graph(args.model)
    saver.restore(sess, args.model[:-5])  # Load corresponding checkpoint
    print("Model restored successfully.")
except Exception as e:
    print(f"Error restoring model: {e}")
    exit(1)

# Access model tensors
try:
    graph = tf.compat.v1.get_default_graph()
    input = graph.get_tensor_by_name("model_input:0")
    seq_len = graph.get_tensor_by_name("seq_lengths:0")
    rnn_keep_prob = graph.get_tensor_by_name("keep_prob:0")
    height_tensor = graph.get_tensor_by_name("input_height:0")
    width_reduction_tensor = graph.get_tensor_by_name("width_reduction:0")
    logits = tf.compat.v1.get_collection("logits")[0]

    # Retrieve constants from the model
    WIDTH_REDUCTION, HEIGHT = sess.run([width_reduction_tensor, height_tensor])
    print(f"Width reduction: {WIDTH_REDUCTION}, Height: {HEIGHT}")

    # Define the decoding operation
    decoded, _ = tf.nn.ctc_greedy_decoder(logits, seq_len)
    print("Decoding operation defined.")
except Exception as e:
    print(f"Error accessing model tensors: {e}")
    exit(1)

# Preprocess image
try:
    image = cv2.imread(args.image, 0)  # Grayscale image
    if image is None:
        raise ValueError("Image could not be loaded. Check the path.")
    image = mozart_utils.resize(image, HEIGHT)
    image = mozart_utils.normalize(image)
    image = np.asarray(image).reshape(1, image.shape[0], image.shape[1], 1)
    print(f"Image preprocessed. Shape: {image.shape}")
except Exception as e:
    print(f"Error preprocessing image: {e}")
    exit(1)

# Calculate sequence lengths
seq_lengths = [image.shape[2] / WIDTH_REDUCTION]
if not seq_lengths[0].is_integer():
    print("Warning: Sequence length is not an integer. Adjusting...")
seq_lengths = [int(seq_lengths[0])]

# Predict
try:
    prediction = sess.run(decoded,
                          feed_dict={
                              input: image,
                              seq_len: seq_lengths,
                              rnn_keep_prob: 1.0,
                          })
    str_predictions = mozart_utils.sparse_tensor_to_strs(prediction)
    result = [int2word.get(w, "Unknown") for w in str_predictions[0]]
    print(result)
except Exception as e:
    print(f"Error during prediction: {e}")
    exit(1)
