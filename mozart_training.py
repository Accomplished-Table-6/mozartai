import tensorflow as tf
from primus import CTC_PriMuS
import mozart_utils
import mozart_model
import argparse
import os

# Check GPU availability and configure memory growth
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

parser = argparse.ArgumentParser(description='Train model.')
parser.add_argument('-corpus', dest='corpus', type=str, required=True, help='Path to the corpus.')
parser.add_argument('-set', dest='set', type=str, required=True, help='Path to the set file.')
parser.add_argument('-save_model', dest='save_model', type=str, required=True, help='Path to save the model.')
parser.add_argument('-vocabulary', dest='voc', type=str, required=True, help='Path to the vocabulary file.')
parser.add_argument('-semantic', dest='semantic', action="store_true", default=False)
args = parser.parse_args()

# Load primus
primus = CTC_PriMuS(args.corpus, args.set, args.voc, args.semantic, val_split=0.1)

# Parameterization
img_height = 128
params = mozart_model.default_model_params(img_height, primus.vocabulary_size)
max_epochs = 64000
dropout_rate = 0.5

# Model
inputs, seq_len, targets, decoded, loss, rnn_keep_prob = mozart_model.ctc_crnn(params)
optimizer = tf.keras.optimizers.Adam()

# Checkpoint to save and load the model
checkpoint_dir = os.path.dirname(args.save_model)
checkpoint = tf.train.Checkpoint(optimizer=optimizer, model=decoded)

@tf.function
def train_step(batch_inputs, batch_seq_len, batch_targets, dropout_rate):
    with tf.GradientTape() as tape:
        predictions, loss_value = decoded(batch_inputs, training=True)
        loss_value = tf.reduce_mean(loss_value)
    gradients = tape.gradient(loss_value, decoded.trainable_variables)
    optimizer.apply_gradients(zip(gradients, decoded.trainable_variables))
    return loss_value

# Training loop
for epoch in range(max_epochs):
    batch = primus.nextBatch(params)
    loss_value = train_step(batch['inputs'], batch['seq_lengths'], batch['targets'], dropout_rate)

    if epoch % 1000 == 0:
        # Validation
        print(f'Loss value at epoch {epoch}: {loss_value}')
        print('Validating...')

        validation_batch, validation_size = primus.getValidation(params)

        val_idx = 0
        val_ed = 0
        val_len = 0
        val_count = 0

        while val_idx < validation_size:
            mini_batch_inputs = validation_batch['inputs'][val_idx:val_idx + params['batch_size']]
            mini_batch_seq_len = validation_batch['seq_lengths'][val_idx:val_idx + params['batch_size']]

            prediction = decoded(mini_batch_inputs, training=False)
            str_predictions = ctc_utils.sparse_tensor_to_strs(prediction)

            for i, pred in enumerate(str_predictions):
                ed = ctc_utils.edit_distance(pred, validation_batch['targets'][val_idx + i])
                val_ed += ed
                val_len += len(validation_batch['targets'][val_idx + i])
                val_count += 1

            val_idx += params['batch_size']

        print(f'[Epoch {epoch}] {1. * val_ed / val_count} ({100. * val_ed / val_len} SER) from {val_count} samples.')
        print('Saving the model...')
        checkpoint.save(file_prefix=os.path.join(checkpoint_dir, 'ckpt'))
        print('------------------------------')
