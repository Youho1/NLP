import torch

class CBOW(torch.nn.Module):

    def __init__(self, vocab_size, embedding_dim, context_size):
        super(CBOW, self).__init__()
        self.embeddings = torch.nn.Embedding(vocab_size, embedding_dim)
        self.linear1 = torch.nn.Linear(context_size * embedding_dim, 128)
        self.linear2 = torch.nn.Linear(128, vocab_size)

    def forward(self, inputs):
        embeds = self.embeddings(inputs).view((1, -1))
        out = torch.nn.functional.relu(self.linear1(embeds))
        out = self.linear2(out)
        return out