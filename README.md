# Pairs_trading-Capstone

This project has two fold objectives 
- Propose enhanced pair selection model via LSTM layer
- Explore trading strategies through reinforcement learning

## Capstone Flow
Below is the flowchart for the capstone project:
<p align="center">
  <img src="./capstone_flow.jpeg" width="400">
</p>

## Major Checkpoints
There are 4 major checkpoints to the project:
1. Get data of US500 stocks via API which is 5 min interval from 2020 - 2023. [Completed]
2. Check for stationarity-cointegration and add features and target labels to predict. [Completed]
3. LSTM training - We have 2 sequential models
   - predict if cointegration will last or not [Partially Completed]
   - model the hedge ratio future [Partially Completed]
4. We will compare proposed framework, existing rolling OLS and Kalman methods by trading via 1.RL | 2.Threshold based agent  [To start]
