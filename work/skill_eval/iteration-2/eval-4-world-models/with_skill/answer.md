# ICLR 2025 → 2027：world model 投稿涨了多少、由谁推动、谁在降温

## 结论先行

- **涨幅**：明确提到 world model 的投稿从 2025 年的 **120 篇**涨到 2026 年的 **229 篇**，再到 2027 年的 **1,801 篇**，数量约为 2025 年的 15 倍。但 ICLR 总投稿量也在暴涨（11.7k → 19.8k → 43.0k），所以要看占比：每万篇投稿中的 world model 论文从 **103 → 116 → 419**。也就是说，**2025→2026 只涨了约 12%，真正的爆发在 2026→2027，占比翻了约 3.6 倍**（2027 相比 2025 约 4.1 倍）。只统计标题或关键词里写了 world model 的论文，涨幅更大（每万篇 78 → 88 → 364，2027/2026 为 4.1 倍）。去掉 2027 年那批"公式化写作"摘要后，结论不变。
- **推动增长的主要是四个具体方向**，它们合计贡献了 2026→2027 增量的约 2/3：
  1. **世界-动作模型（World Action Model, WAM）/ 视频预测式机器人策略**：这是最大的单一推手，WAM 这个说法 2026 年几乎没人用，2027 年约每 5 篇 world model 论文里就有 1 篇提到它；
  2. **JEPA / 潜空间世界模型 + 规划**（LeWorldModel、DINO-WM、V-JEPA 2-AC 这一路）；
  3. **机器人/导航用的动作条件世界模型**：当作仿真器、策略评测器或 MPC 规划器；
  4. **交互式视频世界模型**：可实时操控、长时记忆、空间一致性，以及相应的评测基准。
- **降温的方向**：严格说没有哪个方向的绝对规模明显缩小，但有几个方向在全部投稿中的占比基本**原地踏步**，在 world model 论文中的份额被快速稀释：
  - **经典 MBRL**：Dreamer 式"在想象中训练策略"，Atari100k、DMC 这类基准，是降温最明显的一个；
  - **LLM 相关的世界模型**：LLM 当环境模拟器、web/GUI agent 的世界模型、LLM 内部世界表征的探测；
  - **纯生成式的自动驾驶世界模型**：occupancy 预测、多视角视频生成；
  - 视频生成方向里偏"物理合理性评测、神经游戏引擎/Minecraft"的子话题。

## 1. 总量：怎么涨的

| 口径 | 2025 | 2026 | 2027 | 2027/2026 | 2027/2025 |
|---|---|---|---|---|---|
| 摘要/标题/关键词提及 world model（含 world-action model、world simulator） | 120（每万篇 103） | 229（116） | 1,801（419） | 3.6× | 4.1× |
| 只算标题或关键词含 world model（"核心"论文） | 91（78） | 175（88） | 1,565（364） | 4.1× | 4.7× |
| 去掉 2027 公式化写作摘要 | 120（103） | 228（116） | 1,017（410） | 3.5× | 4.0× |
| 只算未撤稿、未被 desk reject 的论文（分母同样只算这类投稿） | 94（109） | 164（119） | 1,785（421） | 3.5× | 3.9× |

另外两个旁证。第一，2026 年 world model 论文的接收率是 **33.6%**（以全部投稿为分母，全会为 27.0%；只算有结论的论文则是 47.0% 对 38.8%），说明这个方向 2027 年的扩张之前，审稿人对它的评价已经偏高。第二，从论文角色来看，只是"顺带提一句 world model"的论文占比没有上升（约 12.5% → 10.5% → 9%），所以这次增长不是蹭热词，大多数论文确实以世界模型为主体或核心组件。

## 2. 哪些方向在推动增长

下表是逐篇阅读的结果：2025 年 120 篇全读，2026 年和 2027 年各随机抽 200 篇。每篇按"应用领域 × 世界模型在文中的角色"归入一个互斥方向，再换算成每万篇投稿的估计值。2027 年的抽样误差较大（±约 12–21），所以每个结论都用全量词表计数或主题聚类做了交叉验证（见右两列）。

| 方向 | 在 world model 论文中的占比 2025 / 2026 / 2027 | 每万篇投稿（估计）2025 / 2026 / 2027 | 对 2026→27 增量的贡献 | 全量交叉验证（每万篇投稿） |
|---|---|---|---|---|
| **WAM / 视频预测式机器人（及驾驶）策略** | 1.7% / 6.5% / **15.0%** | 2 / 8 / **63**（±20） | ~18% | "world action model/WAM" 0.9 → 0.5 → **82**；聚类"World action models for robots" 2.6 → 2.5 → 68 |
| **机器人/导航世界模型**（仿真器、策略评测、MPC） | 7.5% / 13.5% / 16.0% | 8 / 16 / **67**（±20） | ~17% | robot/manipulation 25 → 30 → 155；navigation/UAV 6.9 → 7.6 → 33 |
| **潜空间/JEPA 世界模型及规划**（不含机器人专用） | 10.8% / 8.5% / 14.5% | 11 / 10 / **61**（±19） | ~17% | JEPA 0 → 1.0 → **52**；"latent world model" 1.7 → 4.5 → 48；LeWM/DINO-WM/V-JEPA 0.9 → 0.5 → 28；JEPA 聚类 0 → 1.0 → 40 |
| **交互式视频世界模型 / 世界生成与评测** | 10.8% / **21.5%** / 17.5% | 11 / 25 / **73**（±21） | ~16% | "interactive/video world model" 10 → 16 → 66；记忆/长时一致性 6.9 → 12 → 54；聚类"Interactive video world models" 5.1 → 14.6 → 49 |
| 科学/医疗等其他应用（虚拟细胞、MRI、手术、天气…） | 0% / 5.0% / 6.0% | 0 / 6 / 25（±13） | ~6% | — |
| LLM 相关（LLM 当世界模型、agent 世界模型、内部表征） | 14.2% / 11.5% / 7.5% | 15 / 13 / 31（±14） | ~6% | LLM 27 → 30 → 55（只有 1.8×） |
| **经典 MBRL（在想象中训练策略）** | **25.8% / 15.0% / 5.0%** | 27 / 17 / 21（±12） | ~1% | Atari100k/DMC/Crafter 15.4 → 13.6 → 16.3；"model-based RL" 23 → 18 → 25 |
| 自动驾驶生成式世界模型（不含驾驶 WAM） | 9.2% / 4.5% / 1.5% | 9 / 5 / 6（±7） | ~0% | autonomous driving 14 → 10 → 30（2.9×，低于平均）；occupancy 4.3 → 2.0 → 10 |
| 通用方法/理论（非潜空间） | 7.5% / 3.5% / 8.0% | 8 / 4 / 34 | ~10% | — |
| 仅顺带提及 | 12.5% / 10.5% / 9.0% | 13 / 12 / 38 | ~8% | — |

**观察 1：WAM 是 2027 年最突出的新增量。**2026 年已经有"把视频生成模型改造成机器人策略"的工作，例如 Genie Envisioner、Cosmos Policy、UniVLA，但当时它们多以 VLA 或 world model 的名义出现。2027 年这类工作统一叫作 WAM，数量涨了约 8 倍，在 world model 论文中的占比从 6.5% 升到 15%。全量计数里有 354 篇（19.7%）明确提到 WAM，主题聚类"World action models for robots"一个就贡献了全部增量的约 22%。研究重心已经从"造出 WAM"转向**工程化和改进**：推理加速（1Step-WAM、RealtimeWAM、WAMachine）、自我进化/持续学习、3D 化（PointWAM、SpatialWAM）、对抗鲁棒性，同时扩展到驾驶（DriveWeave、OSWAM）和无人机（FG-WVAM、PAIMON）。

**观察 2：表征从"像素视频"回摆到"潜空间 + 动作"。**以逐篇阅读的表征类型看，2026 年是"视频生成即世界模型"的一年：像素视频类占比从 16% 升到 36%，潜空间类从 37.5% 降到 25.5%。到 2027 年，潜空间类回升到 34.5%。JEPA 系（LeWorldModel、DINO-WM、V-JEPA 2-AC 的后续，以及围绕它们的规划接口、表征坍塌、理论、测试时适应等论文）从几乎为零涨到每万篇 52 篇，涨幅仅次于 WAM。

**观察 3：交互式视频世界模型仍在增长，但在 world model 内部的份额已经见顶。**它在 2026 年增长最快，占比从 10.8% 升到 21.5%。2027 年的绝对规模又涨了约 3 倍，与 world model 整体同步，但份额略降到 17.5%。子话题在换挡：长时记忆、空间一致性、实时交互、多人/多智能体世界这些新话题涨幅高于平均（约 4.5 倍）；"视频生成是否符合物理"（1.9 倍）和"神经游戏引擎/Minecraft"（1.3 倍）则明显跑输整体。

## 3. 哪些方向其实在降温

这里的"降温"指在全部投稿中的占比基本持平，同时在 world model 论文中的份额大幅下滑。2027 年几乎所有方向的篇数都在涨，只看篇数会产生误判。

1. **经典 MBRL / Dreamer 式"想象中训练策略"：降温最明显。**它在 world model 论文中的占比从 26% 降到 15% 再到 5%，按每万篇投稿算基本持平（27 → 17 → 21）。全量计数结论一致：Atari100k/DMC/Crafter 一直在每万篇 13–16 篇，去掉公式化写作后 2027/2026 只有 0.96 倍；"model-based RL"这个说法是 23 → 18 → 25（去掉公式化写作后 1.2 倍）；Dreamer/RSSM/TD-MPC 去掉公式化写作后只有 1.5 倍。相关主题聚类的绝对篇数也几乎不动，例如 Offline RL 是 7 → 6 → 7，General deep RL 是 3 → 5 → 2。world model 一词的重心已经从 RL 社区转移到具身/机器人和视频生成社区。
2. **LLM 相关的世界模型：增长明显低于整体。**包括 LLM 当环境模拟器、web/GUI agent 的世界模型、LLM 内部世界表征的探测（Othello 一类）。它在 world model 论文中的占比从 14% 降到 11.5% 再到 7.5%；全量计数里"LLM/language model"的提及率从 27% 降到 13%，每万篇投稿只涨了 1.8 倍，web/GUI agent 世界模型只涨了 1.7 倍，聚类"LLM and embodied task planning"的绝对篇数是 4 → 10 → 13。
3. **自动驾驶：纯生成式世界模型在降温，增长转到了驾驶 WAM。**提到自动驾驶的 world model 论文是每万篇 14 → 10 → 30，2026 年下滑，2027 年回升，但涨幅低于平均，在 world model 中的占比从 13% 降到 7%。逐篇阅读中，"不含策略的驾驶生成世界模型"（occupancy 预测、多视角视频生成）基本没有增长；2027 年的驾驶论文多数是 WAM 或 VLA 风格的"预测未来并输出轨迹"方案。驾驶这一项样本小，2027 年只有个位数，只能看方向，不宜细比。
4. **视频生成里的"物理合理性评测"和"神经游戏引擎/Minecraft"：在交互视频方向内部相对降温**（理由见观察 3）。

## 4. 代表性论文（供核对分类）

- WAM（2027）：[Video Prediction Policy 2](https://openreview.net/forum?id=puc8b9cUyy)、[OpenWAM](https://openreview.net/forum?id=jn7HQWdLuc)、[DriveWeave-Policy（驾驶 WAM）](https://openreview.net/forum?id=PbZLbsq4aU)；2026 年的前身：[Genie Envisioner](https://openreview.net/forum?id=fHLtSxDFKC)
- JEPA / 潜空间规划（2027）：[LeWM++](https://openreview.net/forum?id=RIpEtbedmF)、[MemJEPA](https://openreview.net/forum?id=SrOV8zNnVl)、[A Generalization Theory for JEPA-Based World Models](https://openreview.net/forum?id=tkpkXM7IFR)
- 交互式视频世界模型（2027）：[WorldPlay2](https://openreview.net/forum?id=rK38d8xJlc)、[WorldState](https://openreview.net/forum?id=LLBK9eAXmM)、[WorldRoamBench](https://openreview.net/forum?id=QrVhQvM6H2)
- 机器人世界模型当仿真器/评测器：[WorldOracle（2027）](https://openreview.net/forum?id=43TnxEoIFC)、[ForceWorld（2027）](https://openreview.net/forum?id=pI0XNr6iy1)、[Ctrl-World（2026，接收）](https://openreview.net/forum?id=748bHL2BAv)
- 降温方向示例：经典 MBRL [Drama（2025）](https://openreview.net/forum?id=7XIkRgYjK3) / [NE-Dreamer（2027）](https://openreview.net/forum?id=FYtg63NCjr)；LLM 世界模型 [WMA web agent（2025）](https://openreview.net/forum?id=moWiYJuSGF) / [WorldSimBench（2027）](https://openreview.net/forum?id=5qVqc42f9Y)

## 方法说明

- **哪些论文算 world model 论文**：标题、关键词或摘要匹配 `world model(s)/world modeling`、`world(-)action model` 或 `world simulator(s)`，排除只出现"real-world model / open-world model"的情况；不使用 TL;DR，因为只有 2027 年有。结果为 2025 年 120 篇、2026 年 229 篇、2027 年 1,801 篇，含撤稿和 desk reject。
- **召回检查**："world action model"有 223 篇 2027 论文不含"world model"字样，所以已加入匹配条件。只靠 world model 相关聚类（8、30、161、228）纳入的论文多是泛 JEPA 自监督或一般视频生成，没有纳入。泛称"dynamics model / video prediction"的经典 MBRL 论文没有纳入，因此 MBRL 的绝对量偏低，但三年口径一致。
- **方向怎么判的**：作者逐篇阅读摘要（2025 年全读，2026 年和 2027 年各随机抽 200 篇，共 520 篇），按领域（9 类）、世界模型的角色（7 类）和表征（6 类）打标签，再按固定规则合成为表中的互斥方向。2027 年的抽样份额给出 95% 区间，每万篇的估计值等于样本占比乘以总体规模。随机抽 20 篇复核，约 2–3 篇属于边界情况（例如真实机器人上的离线 MBRL 应归"机器人"还是"RL 基准"），不影响主要结论。
- **稳健性**：2027 年 44% 的 world model 摘要属于公式化写作风格。去掉这部分后重算，总量（3.5 倍）、WAM（175 倍）、JEPA（46 倍）、MBRL 持平（Atari/DMC 0.96 倍）等结论都成立。唯一不稳的是"基准/分析类论文"占比的上升（全量 17%，去掉公式化写作后 10%），所以没有把它当作结论。
- **注意事项**：以上只统计摘要层面写出来的内容，提及不等于实际使用；2027 年还没有审稿结果；方向标签由一位阅读者（本次分析者）完成，没有做第二人复核。
