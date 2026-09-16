
from collections import deque
from tensorflow import keras
import numpy as np


class DQNConfig:
    input_dim = 10  # Example input shape, adjust as needed
    output_dim = 3  # Example output shape, adjust as needed
    gamma = 0.99  # Discount factor
    batch_size = 32
    learning_rate = 0.001
    
    def __str__(self):
        return f"DQNConfig(input_dim={self.input_dim}, output_dim={self.output_dim}, gamma={self.gamma}, batch_size={self.batch_size}, learning_rate={self.learning_rate})"

class QNet(keras.Model):
    def __init__(self, input_dim, output_dim, **kwargs):
        super(QNet, self).__init__(**kwargs)
        
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.network = keras.Sequential([
            keras.layers.Dense(64, activation='relu', input_dim = input_dim),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(8, activation='relu'),
            keras.layers.Dense(output_dim, activation='linear')
        ])

    def forward(self, x):
        x = keras.ops.convert_to_tensor(x)
        return self.network(x)

    def __call__(self, x):
        return self.forward(x)
    
    def get_config(self):
        config = super(QNet, self).get_config()
        config.update({
            'input_dim': self.input_dim,
            'output_dim': self.output_dim
        })
        return config


class DQNAgent():
    def __init__(self, config):
        self.config = config
        self.qnet = QNet(input_dim=config.input_dim, output_dim=config.output_dim)
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

        loss = self.exp_replay()
        print('Loss:', loss)

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



