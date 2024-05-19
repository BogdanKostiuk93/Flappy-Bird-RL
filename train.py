# Импортируем вашу среду
from flapping_bird_gym import FlappingBirdEnv, FlappingBirdEnvNumerical
import d3rlpy
import matplotlib.pyplot as plt
import torch



def ai_learn():
    # env = FlappingBirdEnv(FPS=60, logs=False)
    # eval_env = FlappingBirdEnv(FPS=60, logs=False)
    env = FlappingBirdEnvNumerical(FPS=60, logs=False)
    eval_env = FlappingBirdEnvNumerical(FPS=60, logs=False)

    if torch.cuda.is_available():
        print("GPU доступен.")
        print("GPU Name:", torch.cuda.get_device_name(0))
        device = "cuda:0"
    else:
        print("GPU не доступен.")
        device = "cpu:0"

    # setup algorithm
    dqn = d3rlpy.algos.DQNConfig(
        batch_size=8,
        learning_rate=2.5e-4,
        target_update_interval=100,
        gamma=1,
    ).create(device=device)

    # experience replay buffer
    buffer = d3rlpy.dataset.create_fifo_replay_buffer(limit=100000, env=env)

    # exploration strategy
    # in this tutorial, epsilon-greedy policy with static epsilon=0.3
    explorer = d3rlpy.algos.LinearDecayEpsilonGreedy(start_epsilon=1.0,
                                        end_epsilon=0.01,
                                        duration=100000)

    dqn.fit_online(
        env,
        buffer,
        explorer,
        n_steps=100000,  # train for 100K steps
        eval_env=eval_env,
        n_steps_per_epoch=1000,  # evaluation is performed every 1K steps
        update_start_step=1000,  # parameter update starts after 1K steps
    )

    # Сохраняем обученную модель
    dqn.save_model('dqn_flappy_bird.pt')
    env.close()

ai_learn()