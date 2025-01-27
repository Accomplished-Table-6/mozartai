import tensorflow as tf
import mozart_utils
import cv2
import numpy as np

def decode_music_score(image_path, model_path, voc_file_path):
    """
    Decodes a music score image using a trained model (CTC).

    Parameters:
        image_path (str): Path to the input image.
        model_path (str): Path to the trained model.
        voc_file_path (str): Path to the vocabulary file.

    Returns:
        list: Decoded text from the image as a list of words.
    """
    # Check TensorFlow compatibility
    tf.compat.v1.reset_default_graph()
    sess = tf.compat.v1.InteractiveSession()
    tf.compat.v1.disable_eager_execution()

    # Load vocabulary
    try:
        with open(voc_file_path, 'r') as dict_file:
            dict_list = dict_file.read().splitlines()
            int2word = {idx: word for idx, word in enumerate(dict_list)}
        print(f"Loaded vocabulary with {len(int2word)} entries.")
    except Exception as e:
        raise ValueError(f"Error loading vocabulary: {e}")

    # Restore model
    try:
        saver = tf.compat.v1.train.import_meta_graph(model_path)
        saver.restore(sess, model_path[:-5])  # Load corresponding checkpoint
        print("Model restored successfully.")
    except Exception as e:
        raise ValueError(f"Error restoring model: {e}")

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
        raise ValueError(f"Error accessing model tensors: {e}")

    # Preprocess image
    try:
        image = cv2.imread(image_path, 0)  # Grayscale image
        if image is None:
            raise ValueError("Image could not be loaded. Check the path.")
        image = mozart_utils.resize(image, HEIGHT)
        image = mozart_utils.normalize(image)
        image = np.asarray(image).reshape(1, image.shape[0], image.shape[1], 1)
        print(f"Image preprocessed. Shape: {image.shape}")
    except Exception as e:
        raise ValueError(f"Error preprocessing image: {e}")

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
        return result
    except Exception as e:
        raise ValueError(f"Error during prediction: {e}")
    finally:
        sess.close()

# Example usage
# result = decode_music_score("path/to/image.png", "path/to/model.meta", "path/to/vocabulary.txt")
# print(result)
