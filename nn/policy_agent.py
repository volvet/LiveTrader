import torch
import torch.nn.functional as F
import numpy as np


class PolicyConfig():
    input_dim: int = 30
    output_dim: int = 2
    gamma: float = 0.99
    learning_rate: float = 0.001
    resume: bool = False

class PolicyNetwork(torch.nn.Module):
    CAPABILITY = 1000
    def __init__(self, input_dim, output_dim):
        super(PolicyNetwork, self).__init__()
        self.fc1 = torch.nn.Linear(input_dim, 128)
        self.fc2 = torch.nn.Linear(128, 64)
        self.fc3 = torch.nn.Linear(64, 32)
        self.fc4 = torch.nn.Linear(32, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = self.fc4(x)
        return F.softmax(x, dim=-1)

class PolicyAgent:
    def __init__(self, config):
        self.config = config
        self.policy_network = PolicyNetwork(config.input_dim, config.output_dim)
        self.optimizer = torch.optim.Adam(self.policy_network.parameters(), lr=config.learning_rate)

    def get_action(self, state):
        state = torch.tensor(state, dtype=torch.float32)
        probs = self.policy_network(state)
        action_dist = torch.distributions.Categorical(probs)
        action = action_dist.sample()
        return action.item()

    def update(self, transition_dict):
       reward_list = torch.tensor(np.array(transition_dict['reward']), dtype=torch.float32)
       state_list = torch.tensor(np.array(transition_dict['state']), dtype=torch.float32)
       action_list = torch.tensor(np.array(transition_dict['action']), dtype=torch.int)

       G = 0
       self.optimizer.zero_grad()
       #print(f'reward_list length: {len(reward_list)}')
       for i in reversed(range(len(reward_list))):
           G = reward_list[i] + self.config.gamma * G
           state = state_list[i]
           action = action_list[i].view(-1, 1)
           log_prob = torch.log(self.policy_network(state).gather(1, action))
           loss = -log_prob * G
           loss.backward()
       #print(f"Loss: {loss.item()} G: {G}")
       self.optimizer.step()
