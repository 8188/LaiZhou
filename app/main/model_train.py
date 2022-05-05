import sys
import torch
from app.data.func_store import rd2pd
from app.data.data_pipe import health_pipe
from app.data.parameters import H2_health, Oil_health, Water_health
sys.path.append('app/algorithm/Pytorch-MSCRED-master/')
from utils import generate_signature_matrix_node, generate_train_test_data
from utils.data import load_data
from model.mscred import MSCRED
from main_mscred import train as mscred_train


def mscred_renew():
    df = rd2pd()

    health_renew(df, H2_health.renew_path, H2_health.fe,
            H2_health.period, H2_health.save_path, H2_health.label,
            H2_health.op1, H2_health.op2, H2_health.op3, H2_health.op4)

    health_renew(df, Oil_health.renew_path, Oil_health.fe,
            Oil_health.period, Oil_health.save_path, Oil_health.label,
            Oil_health.op1, Oil_health.op2, Oil_health.op3, Oil_health.op4)

    health_renew(df, Water_health.renew_path, Water_health.fe,
            Water_health.period, Water_health.save_path, Water_health.label,
            Water_health.op1, Water_health.op2, Water_health.op3, Water_health.op4)

      
def health_renew(df, renew_path, fe, period, save_path,
    label, op1, op2, op3, op4):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if len(df) >= 6000:
        df = health_pipe(df, fe, period)
        length = df.shape[1]
        df.to_csv(renew_path + label + '.csv', index=False)
        generate_signature_matrix_node(
            raw_data_path=renew_path + label + '.csv',
            save_data_path=renew_path,
            max_time=length)
        generate_train_test_data(
            save_data_path=renew_path,
            train_end=length, 
            test_start=length, 
            test_end=length)
        dataLoader = load_data(
            train_data_path=renew_path + "matrix_data/train_data/", 
            test_data_path=renew_path + "matrix_data/test_data/")

        mscred = MSCRED(3, 256, op1, op2, op3, op4)
        optimizer = torch.optim.Adam(mscred.parameters(), lr = 0.0002)
        mscred.load_state_dict(
            torch.load(save_path + label + ".pth", map_location=device))
        mscred.to(device)
        
        mscred_train(dataLoader["train"], mscred, optimizer, epochs=1, device=device)
        torch.save(mscred.state_dict(), save_path + label + '.pth')