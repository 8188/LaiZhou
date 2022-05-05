import torch
import torch.nn as nn
import numpy as np
from model.convolution_lstm import ConvLSTM
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def attention(ConvLstm_out):
    attention_w = []
    for k in range(5):
        attention_w.append(torch.sum(torch.mul(ConvLstm_out[k], ConvLstm_out[-1]))/5)
    m = nn.Softmax(dim=-1)
    attention_w = torch.reshape(m(torch.stack(attention_w)), (-1, 5))
    cl_out_shape = ConvLstm_out.shape
    ConvLstm_out = torch.reshape(ConvLstm_out, (5, -1))
    convLstmOut = torch.matmul(attention_w, ConvLstm_out)
    #batch_size convLstmOut = torch.reshape(convLstmOut, (-1, cl_out_shape[1], cl_out_shape[2], cl_out_shape[3]))
    convLstmOut = torch.reshape(convLstmOut, (cl_out_shape[1], cl_out_shape[2], cl_out_shape[3]))
    return convLstmOut

class CnnEncoder(nn.Module):
    def __init__(self, in_channels_encoder):
        super(CnnEncoder, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels_encoder, 32, 3, (1, 1), 1),
            # Conv2d(in_channels, out_channels, kernel_size, stride=1, padding=0...)
            # [in_channel - kenel_siz + 2padding]/stride + 1
            # ([30-3+2*1]/1+1), [30-3+2*1]/1+1) -> (30, 30)
            # 20
            nn.SELU()
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, 3, (2, 2), 1),
            # [30-3+2*1]/2+1 = 15
            # 10
            nn.SELU()
        )    
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, 2, (2, 2), 1),
            # [15-2+2*1]/2+1 = 8
            # 6
            nn.SELU()
        )   
        self.conv4 = nn.Sequential(
            nn.Conv2d(128, 256, 2, (2, 2), 0),
            # [8-2+2*0]/2+1 = 4
            # 3
            nn.SELU()
        )
    def forward(self, X):
        conv1_out = self.conv1(X)
        conv2_out = self.conv2(conv1_out)
        conv3_out = self.conv3(conv2_out)
        conv4_out = self.conv4(conv3_out)
        return conv1_out, conv2_out, conv3_out, conv4_out


class Conv_LSTM(nn.Module):
    def __init__(self):
        super(Conv_LSTM, self).__init__()
        self.conv1_lstm = ConvLSTM(input_channels=32, hidden_channels=[32], 
                                   kernel_size=3, step=5, effective_step=[4])
        self.conv2_lstm = ConvLSTM(input_channels=64, hidden_channels=[64], 
                                   kernel_size=3, step=5, effective_step=[4])
        self.conv3_lstm = ConvLSTM(input_channels=128, hidden_channels=[128], 
                                   kernel_size=3, step=5, effective_step=[4])
        self.conv4_lstm = ConvLSTM(input_channels=256, hidden_channels=[256], 
                                   kernel_size=3, step=5, effective_step=[4])

    def forward(self, conv1_out, conv2_out, 
                conv3_out, conv4_out):
        conv1_lstm_out = self.conv1_lstm(conv1_out)
        conv1_lstm_out = attention(conv1_lstm_out[0][0])
        conv2_lstm_out = self.conv2_lstm(conv2_out)
        conv2_lstm_out = attention(conv2_lstm_out[0][0])
        conv3_lstm_out = self.conv3_lstm(conv3_out)
        conv3_lstm_out = attention(conv3_lstm_out[0][0])
        conv4_lstm_out = self.conv4_lstm(conv4_out)
        conv4_lstm_out = attention(conv4_lstm_out[0][0])
        #batch_sizereturn conv1_lstm_out, conv2_lstm_out, conv3_lstm_out, conv4_lstm_out
        return conv1_lstm_out.unsqueeze(0), conv2_lstm_out.unsqueeze(0), conv3_lstm_out.unsqueeze(0), conv4_lstm_out.unsqueeze(0)

class CnnDecoder(nn.Module):
    def __init__(self, in_channels, op1, op2, op3, op4):
        super(CnnDecoder, self).__init__()
        self.deconv4 = nn.Sequential(
            nn.ConvTranspose2d(in_channels, 128, 2, 2, 0, op4),
            nn.SELU()
        )
        self.deconv3 = nn.Sequential(
            nn.ConvTranspose2d(256, 64, 2, 2, 1, op3), #不同feature需要具体调整
            #nn.ConvTranspose2d(256, 64, 2, 2, 1, 0),
            nn.SELU()
        )
        self.deconv2 = nn.Sequential(
            nn.ConvTranspose2d(128, 32, 3, 2, 1, op2), #修改output_padding:H2-1,Oil-0
            nn.SELU()
        )
        self.deconv1 = nn.Sequential(
            nn.ConvTranspose2d(64, 3, 3, 1, 1, op1),
            nn.SELU()
        )
    
    def forward(self, conv1_lstm_out, conv2_lstm_out, conv3_lstm_out, conv4_lstm_out):
        deconv4 = self.deconv4(conv4_lstm_out)
        # ConvTranspose2d(in_channels, out_channels, kernel_size, stride=1, padding=0, output_padding=0...)
        # output = (input-1)stride+outputpadding -2padding+kernelsize
        # (3-1)*2+0-2*0+2 = 6
        deconv4_concat = torch.cat((deconv4, conv3_lstm_out), dim = 1)
        # 6 6
        deconv3 = self.deconv3(deconv4_concat)
        # (6-1)*2+1-2*1+2 = 11
        deconv3_concat = torch.cat((deconv3, conv2_lstm_out), dim = 1)
        # 10 11->10
        deconv2 = self.deconv2(deconv3_concat)
        # (10-1)*2+1-2*1+3 = 20
        deconv2_concat = torch.cat((deconv2, conv1_lstm_out), dim = 1)
        # 20 20
        deconv1 = self.deconv1(deconv2_concat)
        # (20-1)*1+0-2*1+3 = 20
        return deconv1


class MSCRED(nn.Module):
    def __init__(self, in_channels_encoder, in_channels_decoder, op1, op2, op3, op4):
        super(MSCRED, self).__init__()
        self.cnn_encoder = CnnEncoder(in_channels_encoder)
        self.conv_lstm = Conv_LSTM()
        self.cnn_decoder = CnnDecoder(in_channels_decoder, op1, op2, op3, op4)
    
    def forward(self, x):
        conv1_out, conv2_out, conv3_out, conv4_out = self.cnn_encoder(x)
        #print(conv1_out.shape, conv2_out.shape, conv3_out.shape, conv4_out.shape)
        conv1_lstm_out, conv2_lstm_out, conv3_lstm_out, conv4_lstm_out = self.conv_lstm(
                                conv1_out, conv2_out, conv3_out, conv4_out)

        gen_x = self.cnn_decoder(conv1_lstm_out, conv2_lstm_out, 
                                 conv3_lstm_out, conv4_lstm_out)
        return gen_x


