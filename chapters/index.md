# ML Explained

A post-mortem of deep learning from AlexNet (2012) to today's large language models.

Instead of a timeline, the book takes a modern Transformer apart and gives each building block its own chapter, tracing how it evolved and asking why each replacement won. Vision and language appear as two branches inside each lineage, merging where the Transformer unified them.

Every chapter is a runnable notebook: an architecture diagram, 30 to 100 lines of PyTorch, a small experiment that runs on a laptop CPU or a free Colab GPU, and a post-mortem that tags each claim as **[established]**, **[likely]** or **[speculative]**.

## Chapters

| # | Chapter | Status |
| --- | --- | --- |
| 0 | Prologue: why deep learning stalled before 2012 | planned |
| 1 | [Anatomy of a modern Transformer](01-anatomy/index.ipynb) | draft |
| 2 | Tokens and embeddings | planned |
| 3 | Position encoding | planned |
| 4 | Token mixing: convolution, recurrence, attention | planned |
| 5 | [Channel mixing: sigmoid MLP to Mixture of Experts](05-channel-mixing/index.ipynb) | draft |
| 6 | Normalization | planned |
| 7 | Residual connections | planned |
| 8 | Objective and loss | planned |
| 9 | Optimizer | planned |
| 10 | Learning-rate schedule | planned |
| 11 | Initialization and regularization | planned |
| 12 | Scale: scaling laws, in-context learning, emergence | planned |
| 13 | Post-training: instruction tuning, RLHF, RL for reasoning | planned |
| 14 | Inference and use: test-time compute, tools, agents | planned |
| 15 | Epilogue: what keeps winning | planned |

## The evolution tree

A `*` marks a major step (a full deep dive); everything else is a short note. Years are approximate until each chapter checks them against the papers.

```
Modern Transformer (2026)
│
├── ARCHITECTURE
│   ├── Tokens & embeddings
│   │   ├── language: one-hot → word2vec* (2013) → BPE (2016) → SentencePiece, byte-level BPE (2018-19)
│   │   ├── vision:   raw pixels into CNNs (2012) → image patches, ViT* (2020)
│   │   └── merged:   multimodal tokens (2022-24)
│   ├── Position encoding
│   │   ├── implicit: convolution windows (vision), recurrence order (language)
│   │   └── explicit: sinusoidal (2017) → learned (2018) → relative (2018) → RoPE* (2021), ALiBi (2021) → RoPE scaling (2023)
│   ├── Token mixing
│   │   ├── vision:   convolution, AlexNet* (2012) → VGG, Inception (2014)
│   │   ├── language: RNN → LSTM seq2seq* (2014) → Bahdanau attention* (2014)
│   │   ├── merged:   multi-head self-attention, Transformer* (2017) → ViT (2020)
│   │   ├── cheaper:  MQA (2019) → GQA (2023) → MLA (2024); FlashAttention (2022); sliding window (2020-23)
│   │   └── rival:    state-space models, Mamba (2023)
│   ├── Channel mixing (feed-forward)
│   │   ├── activations*: sigmoid, tanh → ReLU (2010-12) → GELU (2016) → Swish (2017) → SwiGLU (2020)
│   │   └── sparsity:     sparsely gated MoE* (2017) → Switch (2021) → Mixtral (2023) → DeepSeekMoE (2024)
│   ├── Normalization
│   │   └── none → BatchNorm* (2015) → LayerNorm (2016) → pre-norm (2019-20) → RMSNorm (2019) → QK-norm (2023)
│   └── Residual connections
│       └── highway nets (2015) → ResNet* (2015) → pre-norm residual stream (2019) → residual-stream view (2021)
│
├── TRAINING RECIPE
│   ├── Objective & loss
│   │   ├── supervised: softmax cross-entropy (AlexNet, 2012)
│   │   ├── language:   skip-gram (2013) → teacher forcing (2014) → masked LM, BERT* / next-token, GPT* (2018)
│   │   ├── vision:     VAE (2013) → GAN* (2014) → diffusion* (2020)
│   │   └── merged:     contrastive image-text, CLIP* (2021)
│   ├── Optimizer
│   │   └── SGD + momentum → AdaGrad (2011), RMSProp (2012) → Adam* (2014) → AdamW (2017) → Lion, Shampoo, Muon (2023-24)
│   ├── Learning-rate schedule
│   │   └── step decay → warmup + cosine* (2016-17) → warmup-stable-decay (2024), schedule-free (2024)
│   └── Initialization & regularization
│       └── Xavier (2010) → He (2015); dropout (2012), augmentation; weight decay; muP (2022)
│
└── BEYOND THE BLOCK
    ├── Scale:           scaling laws* (2020) → Chinchilla (2022); in-context learning* (GPT-3, 2020); emergence (2022)
    ├── Post-training:   instruction tuning (2021-22) → RLHF* (2022) → DPO (2023) → RL on verifiable rewards* (2024-25)
    └── Inference & use: chain of thought (2022) → test-time compute (2024); tool use & agents (2023-26)
```
