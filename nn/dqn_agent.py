
import os
import sys
import warnings
from collections import deque
import keras
import numpy as np
from pathlib import Path

# Ensure imports like "from utils..." work no matter where this script is run from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class DQNConfig:
    input_dim = 10  # Example input shape, adjust as needed
    output_dim = 3  # Example output shape, adjust as needed
    gamma = 0.99  # Discount factor
    batch_size = 32
    learning_rate = 0.001
    
    def __str__(self):
        return f"DQNConfig(input_dim={self.input_dim}, output_dim={self.output_dim}, gamma={self.gamma}, batch_size={self.batch_size}, learning_rate={self.learning_rate})"

class DQNAgent():
    def __init__(self, config):
        self.config = config
        self.model_name = "model_dqn_v0.keras"
        
        if os.path.exists(str(PROJECT_ROOT) + "/models/" + self.model_name):
            print("Loading existing model from " + str(PROJECT_ROOT) + "/models/" + self.model_name)
            self.qnet = keras.models.load_model(str(PROJECT_ROOT) + "/models/" + self.model_name)
        else:
            self.qnet = keras.Sequential([
                    keras.Input(shape = (config.input_dim,)),
                    keras.layers.Dense(64, activation='relu'),
                    keras.layers.Dense(32, activation='relu'),
                    keras.layers.Dense(8, activation='relu'),
                    keras.layers.Dense(config.output_dim, activation='linear')])
        self.qnet.compile(loss='mse', optimizer=keras.optimizers.Adam(learning_rate=config.learning_rate))
        self.target_qnet = keras.models.clone_model(self.qnet)
        self.replay_buffer = deque(maxlen = 1000)

    def get_action(self, state, epsilon=0.0):
        if np.random.rand() < epsilon:
            return np.random.randint(self.qnet.output_shape[-1])
        else:
            q_values = self.qnet(state)
            return np.argmax(q_values.numpy())

    def update(self, state, action, reward, next_state, done):
        self.replay_buffer.append((state, action, reward, next_state, done))

        if len(self.replay_buffer) < self.config.batch_size:
            return np.nan

        loss = self.exp_replay()
        return loss
        
    def save(self):
        model_dir = PROJECT_ROOT / "models"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / self.model_name

        # NumPy 2 can emit this warning from TensorFlow/Keras internals during save.
        # If warnings are treated as errors, training stops here.
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"__array__ implementation doesn't accept a copy keyword.*",
                category=DeprecationWarning,
            )
            self.qnet.save(model_path)

    def exp_replay(self):
        loss = 0
        batch = []
        l = len(self.replay_buffer)
        batch_size = self.config.batch_size
        for i in range(l - batch_size + 1, l):
            batch.append(self.replay_buffer[i])
        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                target += self.config.gamma * np.max(self.target_qnet(next_state).numpy())
            target_f = self.qnet(state).numpy()
            target_f[0][action] = target
            history = self.qnet.fit(state, target_f, epochs=1, verbose=0)
            loss = history.history['loss'][0]

        self.target_qnet.set_weights(self.qnet.get_weights())
        return loss



