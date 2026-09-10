import gymnasium as gym


class TradeEnv(gym.Env):
    def __init__(self, df, window_size, frame_bound, render_mode=None):
        self.df = df
        self.window_size = window_size
        self.frame_bound = frame_bound
        self.render_mode = render_mode

    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)


    def step(self, action):
        pass
