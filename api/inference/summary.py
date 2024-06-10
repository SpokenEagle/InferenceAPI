import os
# import kagglehub
import sys

sys.path.append('gemma_pytorch')
# sys.path.insert(0, 'C:/Users/stude/PycharmProjects/pythonProject')
from api.inference.gemma_pytorch.gemma.gemma.config import get_config_for_7b, get_config_for_2b
from .gemma_pytorch.gemma.model import GemmaForCausalLM
# import torch


# from api.models import test_session


# kagglehub.login()

class Summarizer:
    def __init__(self):
        VARIANT = '2b-it'  # @param ['2b', '2b-it', '7b', '7b-it', '7b-quant', '7b-it-quant']
        MACHINE_TYPE = 'cuda'  # @param ['cuda', 'cpu']
        # Load model weights
        weights_dir = r'C:\Users\stude\.cache\kagglehub\models\google\gemma\pyTorch\2b-it\2' # kagglehub.model_download(f'google/gemma/pyTorch/{VARIANT}')
        # print("weights dir", weights_dir)
        # Ensure that the tokenizer is present
        tokenizer_path = os.path.join(weights_dir, 'tokenizer.model')
        assert os.path.isfile(tokenizer_path), 'Tokenizer not found!'

        # Ensure that the checkpoint is present
        ckpt_path = os.path.join(weights_dir, f'gemma-{VARIANT}.ckpt')
        assert os.path.isfile(ckpt_path), 'PyTorch checkpoint not found!'
        model_config = get_config_for_2b() if "2b" in VARIANT else get_config_for_7b()
        model_config.tokenizer = tokenizer_path
        model_config.quant = 'quant' in VARIANT

        # Instantiate the model and load the weights.
        torch.set_default_dtype(model_config.get_dtype())
        self.device = torch.device(MACHINE_TYPE)
        model = GemmaForCausalLM(model_config)
        model.load_weights(ckpt_path)
        self.model = model.to(self.device).eval()
        self.text = '''The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 Englishto-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data. Recurrent neural networks, long short-term memory and gated recurrent neural networks in particular, have been firmly established as state of the art approaches in sequence modeling and transduction problems such as language modeling and machine translation. Numerous efforts have since continued to push the boundaries of recurrent language models and encoder-decoder architectures. Recurrent models typically factor computation along the symbol positions of the input and output sequences. Aligning the positions to steps in computation time, they generate a sequence of hidden states ht, as a function of the previous hidden state ht1 and the input for position t. This inherently sequential nature precludes parallelization within training examples, which becomes critical at longer sequence lengths, as memory constraints limit batching across examples. Recent work has achieved significant improvements in computational efficiency through factorization tricks and conditional computation, while also improving model performance in case of the latter. The fundamental constraint of sequential computation, however, remains. Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks, allowing modeling of dependencies without regard to their distance in the input or output sequences. In all but a few cases, however, such attention mechanisms are used in conjunction with a recurrent network. In this work we propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output. The Transformer allows for significantly more parallelization and can reach a new state of the art in translation quality after being trained for as little as twelve hours on eight P100 GPUs. Background The goal of reducing sequential computation also forms the foundation of the Extended Neural GPU, ByteNet and ConvS2S, all of which use convolutional neural networks as basic building block, computing hidden representations in parallel for all input and output positions. In these models, the number of operations required to relate signals from two arbitrary input or output positions grows in the distance between positions, linearly for ConvS2S and logarithmically for ByteNet. This makes it more difficult to learn dependencies between distant positions . In the Transformer this is reduced to a constant number of operations, albeit at the cost of reduced effective resolution due to averaging attention-weighted positions, an effect we counteract with Multi-Head Attention as described in section 3.2. Self-attention, sometimes called intra-attention is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence. Self-attention has been used successfully in a variety of tasks including reading comprehension, abstractive summarization, textual entailment and learning task-independent sentence representations. End-to-end memory networks are based on a recurrent attention mechanism instead of sequencealigned recurrence and have been shown to perform well on simple-language question answering and language modeling tasks. To the best of our knowledge, however, the Transformer is the first transduction model relying entirely on self-attention to compute representations of its input and output without using sequencealigned RNNs or convolution. In the following sections, we will describe the Transformer, motivate self-attention and discuss its advantages over models. Model Architecture Most competitive neural sequence transduction models have an encoder-decoder structure. Here, the encoder maps an input sequence of symbol representations x1, ..., xn to a sequence of continuous representations z z1, ..., zn. Given z, the decoder then generates an output sequence y1, ..., ym of symbols one element at a time. At each step the model is auto-regressive, consuming the previously generated symbols as additional input when generating the next. The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder, shown in the left and right halves of Figure 1, respectively. Encoder and Decoder Stacks Encoder The encoder is composed of a stack of N 6 identical layers. Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, positionwise fully connected feed-forward network. We employ a residual connection around each of the two sub-layers, followed by layer normalization. That is, the output of each sub-layer is LayerNormx Sublayerx, where Sublayerx is the function implemented by the sub-layer itself. To facilitate these residual connections, all sub-layers in the model, as well as the embedding layers, produce outputs of dimension dmodel 512. Decoder The decoder is also composed of a stack of N 6 identical layers. In addition to the two sub-layers in each encoder layer, the decoder inserts a third sub-layer, which performs multi-head attention over the output of the encoder stack. Similar to the encoder, we employ residual connections around each of the sub-layers, followed by layer normalization. We also modify the self-attention sub-layer in the decoder stack to prevent positions from attending to subsequent positions. This masking, combined with fact that the output embeddings are offset by one position, ensures that the predictions for position i can depend only on the known outputs at positions less than i. Attention An attention function can be described as mapping a query and a set of key-value pairs to an output, where the query, keys, values, and output are all vectors. The output is computed as a weighted sum of the values, where the weight assigned to each value is computed by a compatibility function of the query with the corresponding key. Scaled Dot-Product Attention We call our particular attention Scaled Dot-Product Attention Figure 2. The input consists of queries and keys of dimension dk, and values of dimension dv. We compute the dot products of the query with all keys, divide each by dk, and apply a softmax function to obtain the weights on the values. In practice, we compute the attention function on a set of queries simultaneously, packed together into a matrix Q. The keys and values are also packed together into matrices K and V . We compute the matrix of outputs as AttentionQ, K, V softmaxQKT dk V 1 The two most commonly used attention functions are additive attention, and dot-product multiplicative attention. Dot-product attention is identical to our algorithm, except for the scaling factor of 1 dk . Additive attention computes the compatibility function using a feed-forward network with a single hidden layer. While the two are similar in theoretical complexity, dot-product attention is much faster and more space-efficient in practice, since it can be implemented using highly optimized matrix multiplication code. While for small values of dk the two mechanisms perform similarly, additive attention outperforms dot product attention without scaling for larger values of dk. We suspect that for large values of dk, the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients 4 . To counteract this effect, we scale the dot products by 1 dk . 3.2.2 Multi-Head Attention Instead of performing a single attention function with dmodel-dimensional keys, values and queries, we found it beneficial to linearly project the queries, keys and values h times with different, learned linear projections to dk, dk and dv dimensions, respectively. On each of these projected versions of queries, keys and values we then perform the attention function in parallel, yielding dv-dimensional 4To illustrate why the dot products get large, assume that the components of q and k are independent random variables with mean 0 and variance 1. Then their dot product, q k Pdk i1 qiki, has mean 0 and variance dk. Applications of Attention in our Model The Transformer uses multi-head attention in three different ways In encoder-decoder attention layers, the queries come from the previous decoder layer, and the memory keys and values come from the output of the encoder. This allows every position in the decoder to attend over all positions in the input sequence. This mimics the typical encoder-decoder attention mechanisms in sequence-to-sequence models such as. The encoder contains self-attention layers. In a self-attention layer all of the keys, values and queries come from the same place, in this case, the output of the previous layer in the encoder. Each position in the encoder can attend to all positions in the previous layer of the encoder. Similarly, self-attention layers in the decoder allow each position in the decoder to attend to all positions in the decoder up to and including that position. We need to prevent leftward information flow in the decoder to preserve the auto-regressive property. We implement this inside of scaled dot-product attention by masking out setting to all values in the input of the softmax which correspond to illegal connections. Why Self-Attention In this section we compare various aspects of self-attention layers to the recurrent and convolutional layers commonly used for mapping one variable-length sequence of symbol representations x1, ..., xn to another sequence of equal length z1, ..., zn, with xi , zi R d , such as a hidden layer in a typical sequence transduction encoder or decoder. Motivating our use of self-attention we consider three desiderata. One is the total computational complexity per layer. Another is the amount of computation that can be parallelized, as measured by the minimum number of sequential operations required. The third is the path length between long-range dependencies in the network. Learning long-range dependencies is a key challenge in many sequence transduction tasks. One key factor affecting the ability to learn such dependencies is the length of the paths forward and backward signals have to traverse in the network. The shorter these paths between any combination of positions in the input and output sequences, the easier it is to learn long-range dependencies . Hence we also compare the maximum path length between any two input and output positions in networks composed of the different layer types. As noted in Table 1, a self-attention layer connects all positions with a constant number of sequentially executed operations, whereas a recurrent layer requires On sequential operations. In terms of computational complexity, self-attention layers are faster than recurrent layers when the sequence 6 length n is smaller than the representation dimensionality d, which is most often the case with sentence representations used by state-of-the-art models in machine translations, such as word-piece and byte-pair representations. To improve computational performance for tasks involving very long sequences, self-attention could be restricted to considering only a neighborhood of size r in the input sequence centered around the respective output position. This would increase the maximum path length to Onr. We plan to investigate this approach further in future work. A single convolutional layer with kernel width k n does not connect all pairs of input and output positions. Doing so requires a stack of Onk convolutional layers in the case of contiguous kernels, or Ologkn in the case of dilated convolutions , increasing the length of the longest paths between any two positions in the network. Convolutional layers are generally more expensive than recurrent layers, by a factor of k. Separable convolutions , however, decrease the complexity considerably, to Ok n d n d 2 . Even with k n, however, the complexity of a separable convolution is equal to the combination of a self-attention layer and a point-wise feed-forward layer, the approach we take in our model. As side benefit, self-attention could yield more interpretable models. We inspect attention distributions from our models and present and discuss examples in the appendix. Not only do individual attention heads clearly learn to perform different tasks, many appear to exhibit behavior related to the syntactic and semantic structure of the sentences. 5 Training This section describes the training regime for our models. 5.1 Training Data and Batching We trained on the standard WMT 2014 English-German dataset consisting of about 4.5 million sentence pairs. Sentences were encoded using byte-pair encoding , which has a shared sourcetarget vocabulary of about 37000 tokens. For English-French, we used the significantly larger WMT 2014 English-French dataset consisting of 36M sentences and split tokens into a 32000 word-piece vocabulary . Sentence pairs were batched together by approximate sequence length. Each training batch contained a set of sentence pairs containing approximately 25000 source tokens and 25000 target tokens. 5.2 Hardware and Schedule We trained our models on one machine with 8 NVIDIA P100 GPUs. For our base models using the hyperparameters described throughout the paper, each training step took about 0.4 seconds. We trained the base models for a total of 100,000 steps or 12 hours. For our big models,described on the bottom line of table 3, step time was 1.0 seconds. The big models were trained for 300,000 steps 3.5 days. 5.3 Optimizer We used the Adam optimizer with 1 0.9, 2 0.98 and 109 . We varied the learning rate over the course of training, according to the formula lrate d 0.5 model minstepnum0.5 , stepnum warmupsteps1.5 3 This corresponds to increasing the learning rate linearly for the first warmupsteps training steps, and decreasing it thereafter proportionally to the inverse square root of the step number. We used warmupsteps 4000. 5.4 Regularization We employ three types of regularization during training Results 6.1 Machine Translation On the WMT 2014 English-to-German translation task, the big transformer model Transformer big in Table 2 outperforms the best previously reported models including ensembles by more than 2.0 BLEU, establishing a new state-of-the-art BLEU score of 28.4. The configuration of this model is listed in the bottom line of Table 3. Training took 3.5 days on 8 P100 GPUs. Even our base model surpasses all previously published models and ensembles, at a fraction of the training cost of any of the competitive models. On the WMT 2014 English-to-French translation task, our big model achieves a BLEU score of 41.0, outperforming all of the previously published single models, at less than 14 the training cost of the previous state-of-the-art model. The Transformer big model trained for English-to-French used dropout rate Pdrop 0.1, instead of 0.3. For the base models, we used a single model obtained by averaging the last 5 checkpoints, which were written at 10-minute intervals. For the big models, we averaged the last 20 checkpoints. We used beam search with a beam size of 4 and length penalty 0.6 . These hyperparameters were chosen after experimentation on the development set. We set the maximum output length during inference to input length 50, but terminate early when possible . Table 2 summarizes our results and compares our translation quality and training costs to other model architectures from the literature. We estimate the number of floating point operations used to train a model by multiplying the training time, the number of GPUs used, and an estimate of the sustained single-precision floating-point capacity of each GPU 5 . 6.2 Model Variations To evaluate the importance of different components of the Transformer, we varied our base model in different ways, measuring the change in performance on English-to-German translation on the development set, newstest2013. We used beam search as described in the previous section, but no checkpoint averaging. We present these results in Table 3. In Table 3 rows A, we vary the number of attention heads and the attention key and value dimensions, keeping the amount of computation constant, as described in Section 3.2.2. While single-head attention is 0.9 BLEU worse than the best setting, quality also drops off with too many heads. In Table 3 rows B, we observe that reducing the attention key size dk hurts model quality. This suggests that determining compatibility is not easy and that a more sophisticated compatibility function than dot product may be beneficial. We further observe in rows C and D that, as expected, bigger models are better, and dropout is very helpful in avoiding over-fitting. In row E we replace our sinusoidal positional encoding with learned positional embeddings , and observe nearly identical results to the base model.In this work, we presented the Transformer, the first sequence transduction model based entirely on attention, replacing the recurrent layers most commonly used in encoder-decoder architectures with multi-headed self-attention. For translation tasks, the Transformer can be trained significantly faster than architectures based on recurrent or convolutional layers. On both WMT 2014 English-to-German and WMT 2014 English-to-French translation tasks, we achieve a new state of the art. In the former task our best model outperforms even all previously reported ensembles. We are excited about the future of attention-based models and plan to apply them to other tasks. We plan to extend the Transformer to problems involving input and output modalities other than text and to investigate local, restricted attention mechanisms to efficiently handle large inputs and outputs such as images, audio and video. Making generation less sequential is another research goals of ours.'''
        self.USER_CHAT_TEMPLATE = '<start_of_turn>user\n{prompt}<end_of_turn>\n'
        self.MODEL_CHAT_TEMPLATE = '<start_of_turn>model\n{prompt}<end_of_turn>\n'

    def summarize(self, text):
        # text = self.text
        prompt = (
                self.USER_CHAT_TEMPLATE.format(
                    prompt='Summarize the following scientific literature text: {}'.format(text)
                )
                + '<start_of_turn>model\n'
        )
        # print('Chat prompt:\n', prompt)
        # print(prompt)
        return self.model.generate(
            prompt,
            device=self.device,
            output_len=550,
        )

    def prepare_template(self, query, previous_chat):
        chat = ''
        for i in previous_chat:
            chat += self.USER_CHAT_TEMPLATE.format(prompt=i.user)
            chat += self.MODEL_CHAT_TEMPLATE.format(prompt=i.model)

        chat += self.USER_CHAT_TEMPLATE.format(prompt=query) + '<start_of_turn>model\n'
        # print(chat)
        return chat

    def reply(self, query, previous_chat):
        prompt = self.prepare_template(query, previous_chat)
        return self.model.generate(
            prompt,
            device=self.device,
            output_len=550,
        )
