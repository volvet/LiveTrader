
from collections import deque
from tensorflow import keras
import numpy as np


class DQNConfig:
    input_shape = (10,)  # Example input shape, adjust as needed
    output_shape = 3  # Example output shape, adjust as needed
    gamma = 0.99  # Discount factor
    batch_size = 32
    learning_rate = 0.001

class QNet(keras.Model):
    def __init__(self, input_shape, output_shape):
        super(QNet, self).__init__()

        self.network = keras.Sequential([
            keras.layers.Dense(64, activation='relu', input_shape=input_shape),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(8, activation='relu'),
            keras.layers.Dense(output_shape, activation='linear')
        ])

    def forward(self, x):
        return self.network(x)

    def __call__(self, x):
        return self.forward(x)


class DQNAgent():
    def __init__(self, config):
        self.config = config
        self.qnet = QNet(input_shape=config.input_shape, output_shape=config.output_shape)
        self.qnet.compile(loss='mse', optimizer=keras.optimizers.Adam(learning_rate=config.learning_rate))
        self.target_qnet = keras.models.clone_model(self.qnet)
        self.replay_buffer = deque(maxlen = 1000)

    def get_action(self, state, epsilon=0.0):
        if np.random.rand() < epsilon:
            return np.random.randint(self.qnet.network.output_shape[-1])
        else:
            q_values = self.qnet(state)
            return np.argmax(q_values.numpy())

    def update(self, state, action, reward, next_state, done):
        self.replay_buffer.append((state, action, reward, next_state, done))

        if len(self.replay_buffer) < self.config.batch_size:
            return

        self.exp_replay()

    def exp_replay(self):
        loss = 0
        batch = np.array(self.replay_buffer[-self.config.batch_size:])
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



