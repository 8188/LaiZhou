import torch
# import torch.nn as nn
from tqdm import tqdm
from model.mscred import MSCRED
from utils.data import load_data
import numpy as np
import os

def train(dataLoader, model, optimizer, epochs, device):
    model = model.to(device)
    print("------training on {}-------".format(device))
    for epoch in range(epochs):
        train_l_sum,n = 0.0, 0
        for x in tqdm(dataLoader):
            x = x.to(device)
            x = x.squeeze()
            #batch_sizex = x.reshape(-1, 3, 20, 20)
            #print(type(x))
            l = torch.mean((model(x)-x[-1].unsqueeze(0))**2)
            train_l_sum += l
            optimizer.zero_grad()
            l.backward()
            optimizer.step()
            n += 1
            #print("[Epoch %d/%d][Batch %d/%d] [loss: %f]" % (epoch+1, epochs, n, len(dataLoader), l.item()))
            
        print("[Epoch %d/%d] [loss: %f]" % (epoch+1, epochs, train_l_sum/n))

def test(dataLoader, model, device, reconstructed_data_path, test_start):
    #print("------Testing-------")
    index = test_start
    loss_list = []
    criterion = torch.nn.MSELoss()
    with torch.no_grad():
        for x in dataLoader:
            x = x.to(device)
            x = x.squeeze()
            #batch_sizex = x.reshape(-1, 3, 20, 20) 
            reconstructed_matrix = model(x) 
            path_temp = os.path.join(reconstructed_data_path, 'reconstructed_data_' + str(index) + ".npy")
            if not os.path.exists(reconstructed_data_path):
                os.makedirs(reconstructed_data_path)
            np.save(path_temp, reconstructed_matrix.cpu().detach().numpy())
            #l = criterion(reconstructed_matrix, x[-1].unsqueeze(0)).mean()
            #loss_list.append(l)
            #print("[test_index %d] [loss: %f]" % (index, l.item()))
            index += 1


if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device is", device)
    dataLoader = load_data()
    mscred = MSCRED(3, 256)

    # 训练阶段
    mscred.load_state_dict(torch.load("./checkpoints/model2.pth"))
    optimizer = torch.optim.Adam(mscred.parameters(), lr = 0.0002)
    #train(dataLoader["train"], mscred, optimizer, 10, device)
    print("保存模型中....")
    if not os.path.exists('./checkpoints'): os.makedirs('./checkpoints')
    torch.save(mscred.state_dict(), "./checkpoints/model2.pth")

    # # 测试阶段
    if not os.path.exists('./data/matrix_data/reconstructed_data'): os.makedirs('./data/matrix_data/reconstructed_data')
    mscred.load_state_dict(torch.load("./checkpoints/model2.pth"))
    mscred.to(device)
    reconstructed_data_path = "./data/matrix_data/reconstructed_data/"
    test(dataLoader["test"], mscred, device, reconstructed_data_path)