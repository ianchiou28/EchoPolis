using System.Collections.Generic;
using UnityEngine;

namespace EchoPolis.Core
{
    [System.Serializable]
    public class MBTITypeData
    {
        public string type;
        public string description;
    }

    [CreateAssetMenu(fileName = "MBTIData", menuName = "EchoPolis/MBTI Data")]
    public class MBTIData : ScriptableObject
    {
        [Header("MBTI Types")]
        public List<MBTITypeData> mbtiTypes = new List<MBTITypeData>
        {
            new MBTITypeData { type = "INTJ", description = "建筑师 - 富有想象力和战略性的思想家，一切皆在计划中" },
            new MBTITypeData { type = "INTP", description = "逻辑学家 - 具有创造性的发明家，对知识有着止不住的渴望" },
            new MBTITypeData { type = "ENTJ", description = "指挥官 - 大胆，富有想象力的强势领导者，总能找到或创造解决方法" },
            new MBTITypeData { type = "ENTP", description = "辩论家 - 聪明好奇的思想家，不会放弃任何挑战" },
            new MBTITypeData { type = "INFJ", description = "提倡者 - 安静而神秘，同时鼓舞他人的理想主义者" },
            new MBTITypeData { type = "INFP", description = "调停者 - 诗意，善良的利他主义者，总是热心为正义而战" },
            new MBTITypeData { type = "ENFJ", description = "主人公 - 魅力非凡的领导者，能够使听众着迷" },
            new MBTITypeData { type = "ENFP", description = "竞选者 - 热情，有创造性的社交者，总能找到微笑的理由" },
            new MBTITypeData { type = "ISTJ", description = "物流师 - 实用主义的现实主义者，可靠性无可置疑" },
            new MBTITypeData { type = "ISFJ", description = "守护者 - 非常专注而温暖的守护者，时刻准备保护爱着的人们" },
            new MBTITypeData { type = "ESTJ", description = "总经理 - 出色的管理者，在管理事物或人员方面无与伦比" },
            new MBTITypeData { type = "ESFJ", description = "执政官 - 极有同情心，善于社交的人们，总是热心帮助他人" },
            new MBTITypeData { type = "ISTP", description = "鉴赏家 - 大胆而实际的实验家，擅长使用各种工具" },
            new MBTITypeData { type = "ISFP", description = "探险家 - 灵活，迷人的艺术家，时刻准备探索新的可能性" },
            new MBTITypeData { type = "ESTP", description = "企业家 - 聪明，精力充沛的感知者，真正享受生活在边缘" },
            new MBTITypeData { type = "ESFP", description = "表演者 - 自发的，精力充沛的娱乐者，生活在他们周围从不无聊" }
        };

        public string GetDescription(string mbtiType)
        {
            var data = mbtiTypes.Find(x => x.type == mbtiType);
            return data?.description ?? "未知类型";
        }

        public List<string> GetAllTypes()
        {
            List<string> types = new List<string>();
            foreach (var data in mbtiTypes)
            {
                types.Add(data.type);
            }
            return types;
        }
    }
}