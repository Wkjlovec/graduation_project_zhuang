# 毕业论文写作草稿（摘要 + Abstract + 第1章第1节）

## 摘要

随着互联网技术和移动终端生态的持续演进，论坛系统的使用场景已从单一的信息浏览扩展到学习交流、经验共享、通知触达与协同讨论等多元场景。与此同时，平台侧也面临新的工程挑战。生成式人工智能工具的普及显著提高了内容生产速度，帖子与评论规模快速增长，传统检索与人工运营方式难以持续支撑高效信息获取。系统在双端一致性、鉴权安全、服务扩展与运维复现方面存在实现割裂，导致用户体验与交付质量不稳定。

针对上述问题，本文设计并实现了一个面向高校场景的微服务论坛系统。后端采用 Spring Boot 3 与 Spring Cloud Alibaba，构建网关、认证、论坛、通知、搜索、媒体推荐等服务。系统通过 MySQL 与 Redis 完成持久化与缓存协同，并采用 JWT+Spring Security+会话校验实现登录、刷新、登出闭环。前端基于 Vue 3 实现 PC 与移动双端，完成帖子发布与检索、分区浏览、二级评论、通知已读、分页筛选与异常反馈等核心功能。系统架构按网关接入层、业务服务层、数据与缓存层、双端交互层组织，并配套一键启停、验活、回归测试与缓存基准脚本，形成可重跑、可对照的验证链路。测试结果表明，系统在功能完整性、异常场景处理与性能稳定性方面满足预期，能够支撑高校用户的日常交流与学习协作需求。

**关键词：** 微服务论坛；Spring Boot；Vue 3；JWT；Redis；可复现测试

## Abstract

With the continuous evolution of Internet technologies and mobile terminal ecosystems, forum systems have expanded from single-purpose information browsing to diversified scenarios such as learning exchange, experience sharing, notice dissemination, and collaborative discussion. At the same time, platforms are facing new engineering challenges. The widespread adoption of AI tools has significantly accelerated content production, causing rapid growth in posts and comments, while traditional retrieval and manual operation methods can no longer support efficient information access. In addition, fragmentation in cross-platform consistency, authentication security, service scalability, and operational reproducibility leads to unstable user experience and delivery quality.

To address these issues, this thesis designs and implements a microservice-based forum system for university scenarios. The backend adopts Spring Boot 3 and Spring Cloud Alibaba to build gateway, authentication, forum, notification, search, and media recommendation services. MySQL and Redis are used for persistence and cache collaboration, and a JWT + Spring Security + session-validation mechanism is introduced to complete the full login-refresh-logout cycle. The frontend is built with Vue 3 for both PC and mobile, implementing core functions including post publishing and retrieval, section-based browsing, two-level comments, notification read-state handling, pagination and filtering, and exception feedback. The overall architecture is organized into an access gateway layer, a business service layer, a data-and-cache layer, and a dual-end interaction layer. In addition, one-click startup and shutdown, health verification, regression testing, and cache benchmarking scripts are provided to form a reproducible and comparable validation pipeline. Experimental results show that the system meets expected requirements in functional completeness, exception handling, and performance stability, and can effectively support daily communication and learning collaboration for university users.

**Keywords:** microservice forum; Spring Boot; Vue 3; JWT; Redis; reproducible testing

## 1.1 研究背景与意义

互联网深度融入高校教学与生活后，学生获取信息和参与讨论的方式已经从线下通知和即时群聊逐步转向线上平台协同。论坛系统在这一过程中仍然具有稳定价值，因为它能够把分散在不同时间点的问题、回复和补充说明组织成连续的话题内容，并保留可回查的历史上下文。已有高校论坛相关工作也表明，论坛并不是可有可无的附属页面，而是课程答疑、资源共享和学习交流中的关键基础设施[1][2]。

从社区产品的发展轨迹看，国内用户对论坛形态并不陌生。早期以天涯论坛和百度贴吧为代表的平台，已经形成了按主题聚合讨论并按时间沉淀内容的使用习惯。进入移动互联网阶段后，交流渠道虽然更加丰富，但高校场景中的信息组织问题并没有自然消失，反而因为入口增多而更复杂。教学通知、作业变更、实验环境说明往往同时出现在课程平台、班级群和临时讨论群，信息版本不一致、上下文断裂、历史结论难追溯的情况在实际教学中较为常见，这也是论坛系统仍被反复强调的现实原因。

设想如下场景。某门课程在一周内先后发布实验配置说明、依赖版本修订和提交规则更新。学生在不同渠道分别提问，教师也在不同时间给出补充答复。到周末集中完成作业时，学生很难快速确认哪一条是最终口径，教师则需要重复解释同类问题。这个问题本质上不是信息太少，而是信息没有被持续整理和结构化沉淀。论坛系统在这里的作用，是把零散交流变成可回查的知识链路，并把一次性沟通转化为可复用的教学资产[1][3]。

与此同时，技术层面的挑战也在增加。部分校园论坛虽然能够完成发帖和回帖等基本流程，但在架构扩展、双端一致、权限边界和运维复现方面仍存在明显不足。相关实现案例显示，系统常见问题并不只体现在界面老旧，而更多出现在工程可维护性上，例如模块耦合偏高、状态同步不稳定、后台治理能力不足，以及测试结果难以重跑验证等[3][4][5]。这类问题在用户规模和内容规模持续增长时会被进一步放大。

AI 工具普及后，内容生产速度明显提升，论坛中学习笔记、代码示例和经验总结的数量快速增长，平台获得了更高活跃度，但也面临更高的信息筛选压力。如果系统缺乏稳定的检索能力，缺乏合理的缓存和权限机制，或者缺少可复验的交付流程，用户很容易陷入信息密集但有效内容触达效率偏低的状态。微服务相关研究也指出，架构升级能够提升系统扩展能力，但同时会引入服务协同与治理复杂度，需要在工程实践中通过明确边界和可验证流程加以控制[6]。基于上述背景，面向高校场景开展论坛系统研究具有明确现实意义。系统建设目标不应仅停留在发帖与回帖功能实现，而应进一步关注跨端一致体验、可维护的服务边界、可复现的测试与交付过程，以及在 AI 内容环境下的信息质量治理能力。只有将需求分析、架构设计、功能实现与验证证据统一到同一工程闭环中，论坛系统才能真正成为高校教学交流中的长期有效基础设施。

