import numpy as np
import pickle
import torch
from matplotlib import pyplot as plt
from tqdm import tqdm
from torch import nn
from torch import optim
from torchtext import datasets
from my_adam_optimizer import MyAdamOptimizer


def main():
    num_epochs = 5

    # Load data
    train_data = datasets.IMDB('data/IMDB/', batch_size=128,
                               device=None
                               download=True, train=True)
    data_loader = torch.utils.data.DataLoader(train_data,
                                              batch_size=128,
                                              shuffle=True,
                                              num_workers=4)

    results = {'Adam': [], 'SGDNesterov': [], 'AdaGrad': []}
    colors = {'Adam': 'r', 'SGDNesterov': 'g', 'AdaGrad': 'b'}
    for name in ['Adam', 'SGDNesterov', 'AdaGrad']:
        print('Starting', name)

        # Logistic regression model
        model = nn.Sequential(nn.Linear(784, 10), nn.LogSoftmax(dim=1))
        model.cuda()

        # Negative log likelihood
        criterion = nn.NLLLoss()

        if name == 'Adam':
            optimizer = MyAdamOptimizer(model.parameters())
        elif name == 'SGDNesterov':
            optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9, nesterov=True)
        elif name == 'AdaGrad':
            optimizer = optim.Adagrad(model.parameters())

        for i in tqdm(range(num_epochs)):
            loss = 0
            for x, y in data_loader:
                x = x.cuda()
                y = y.cuda()
                x = x.view(x.shape[0], -1)
                model.zero_grad()
                y_pred = model(x)
                train_loss = criterion(y_pred, y)
                train_loss.backward()
                optimizer.step()
                loss += train_loss.item()
            results[name].append(loss/len(data_loader))

        print(results[name][-1])
        plt.plot(np.arange(num_epochs), results[name], label=name, c=colors[name], linewidth=1)
        pickle.dump(results[name], open(name+'.p', 'wb'))

    plt.xlabel('Epoch')
    plt.ylabel('Training Loss')
    plt.xticks(np.arange(num_epochs))
    plt.title('IMDB BoW Feature Logistic Regression')
    plt.legend()
    plt.savefig('out.png')
    plt.show()


if __name__ == '__main__':
    main()