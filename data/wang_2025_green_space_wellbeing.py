#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/29581631
# DOI: 10.6084/m9.figshare.29581631.v1
# Title: Designing for Well-Being: Exploring Older Adults' Preferences in Community Green Space Design
# Author: zhendong wang
# License: CC BY 4.0
# N=687 participants, 25 items, 1-5 Likert scale
#
# NOTE: Two versions of this dataset exist on Figshare (30353026 and 29581631).
# Item responses and demographics are identical across both versions; v2 (29581631)
# adds timestamps and IP metadata and is used here as the canonical version.
#
# The 25 item columns are in Chinese. They are assigned generic labels item_01..item_25
# with a mapping comment preserved below for future item-text matching.
#
# ITEM MAPPING (original Chinese column -> assigned label):
#   item_01: 1. 绿地座椅数量充足且设计（如带扶手、靠背）分布合理  [Functional: seating]
#   item_02: 2. 绿地提供足够的遮阳设施（如凉亭、树荫）和避雨场所  [Functional: shade/shelter]
#   item_03: 3.绿地内饮水、卫生间等便民服务配套设施便利             [Functional: water/toilet]
#   item_04: 4. 绿地场所内的智能化融入和无障碍设计满足老年人需求    [Functional: smart/accessible]
#   item_05: 1. 绿地内无障碍通道（如坡道、盲道）覆盖全面，让我感到安全便捷  [Safety: barrier-free path]
#   item_06: 2. 绿地的路面防滑设计（如防滑砖）让我感到出行安全      [Safety: anti-slip]
#   item_07: 3. 绿地空间内夜间照明充足，无照明死角，让我感到行走安全 [Safety: night lighting]
#   item_08: 4. 绿地空间的紧急求助设施（如呼叫按钮）配备完善设置合理，让我感到安全 [Safety: emergency]
#   item_09: 1.社区绿地有专门为老年人量身定制的开放式活动交流空间   [Social: activity space]
#   item_10: 2.在社区绿地定期组织适合老年人的活动（如园艺、合唱等）  [Social: organized activities]
#   item_11: 3.社区绿地布局鼓励邻里互动（如环形步道、共享园艺区）   [Social: layout for interaction]
#   item_12: 4.我常在绿地中与他人交流（如聊天、集体活动）            [Social: actual interaction]
#   item_13: 5.与其他年龄群体共享绿地时，我感到被尊重               [Social: intergenerational respect]
#   item_14: 1.从家到社区绿地的步行时间在10分钟以内                 [Accessibility: walking time]
#   item_15: 2.通往社区绿地的出行路径平坦便捷（无台阶、障碍物）      [Accessibility: path quality]
#   item_16: 3.社区绿地入口标识清晰，易于寻找，便于进入             [Accessibility: signage]
#   item_17: 4.社区绿地空间是否具有多入口，便于从不同方向进入        [Accessibility: multiple entries]
#   item_18: 1.智能导览屏或APP帮助我了解绿地设施等                  [Digital: smart guide]
#   item_19: 2.数字化健身器材（如心率监测）提升锻炼安全性            [Digital: smart equipment]
#   item_20: 3. 紧急呼叫系统（如智能手环、智能报警装置）增加安全感   [Digital: emergency call]
#   item_21: 1.在社区绿地活动时，我感到身心放松                     [Well-being: relaxation]
#   item_22: 2.社区绿地减少了我的孤独感和社会孤立感，提升了我的生活满意度 [Well-being: loneliness]
#   item_23: 3.社区绿地适老化设计让我感受到社区对老年人的关怀        [Well-being: care felt]
#   item_24: 4.我对社区的归属感因社区绿地而增强                     [Well-being: belonging]
#   item_25: 5.我愿意向其他老年人推荐使用社区绿地                    [Well-being: recommend]

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

FIGSHARE_FILE_URL = "https://ndownloader.figshare.com/files/56319872"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Mapping from Chinese column names (cols 11-35 in the Excel, 0-indexed) to item labels
ITEM_MAP = {
    '1. 绿地座椅数量充足且设计（如带扶手、靠背）分布合理': 'item_01',
    '2. 绿地提供足够的遮阳设施（如凉亭、树荫）和避雨场所': 'item_02',
    '3.绿地内饮水、卫生间等便民服务配套设施便利': 'item_03',
    '4. 绿地场所内的智能化融入和无障碍设计满足老年人需求': 'item_04',
    '1. 绿地内无障碍通道（如坡道、盲道）覆盖全面，让我感到安全便捷': 'item_05',
    '2. 绿地的路面防滑设计（如防滑砖）让我感到出行安全': 'item_06',
    '3. 绿地空间内夜间照明充足，无照明死角，让我感到行走安全': 'item_07',
    '4. 绿地空间的紧急求助设施（如呼叫按钮）配备完善设置合理，让我感到安全': 'item_08',
    '1.社区绿地有专门为老年人量身定制的开放式活动交流空间（如长椅区、活动广场）便于社交': 'item_09',
    '2.在社区绿地定期组织适合老年人的活动（如园艺、合唱等）': 'item_10',
    '3.社区绿地布局鼓励邻里互动（如环形步道、共享园艺区）': 'item_11',
    '4.我常在绿地中与他人交流（如聊天、集体活动）': 'item_12',
    '5.与其他年龄群体共享绿地时，我感到被尊重': 'item_13',
    '1.从家到社区绿地的步行时间在10分钟以内': 'item_14',
    '2.通往社区绿地的出行路径平坦便捷（无台阶、障碍物）': 'item_15',
    '3.社区绿地入口标识清晰，易于寻找，便于进入': 'item_16',
    '4.社区绿地空间是否具有多入口，便于从不同方向进入': 'item_17',
    '1.智能导览屏或APP帮助我了解绿地设施等': 'item_18',
    '2.数字化健身器材（如心率监测）提升锻炼安全性': 'item_19',
    '3. 紧急呼叫系统（如智能手环、智能报警装置）增加安全感': 'item_20',
    '1.在社区绿地活动时，我感到身心放松': 'item_21',
    '2.社区绿地减少了我的孤独感和社会孤立感，提升了我的生活满意度': 'item_22',
    '3.社区绿地适老化设计让我感受到社区对老年人的关怀': 'item_23',
    '4.我对社区的归属感因社区绿地而增强': 'item_24',
    '5.我愿意向其他老年人推荐使用社区绿地': 'item_25',
}


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Download file
    resp = requests.get(FIGSHARE_FILE_URL, headers=HEADERS)
    resp.raise_for_status()
    df = pd.read_excel(io.BytesIO(resp.content), sheet_name='Sheet1')

    # Person ID: column 序号 (serial number)
    df = df.rename(columns={'序号': 'id'})
    df = df.dropna(subset=['id'])
    df['id'] = pd.to_numeric(df['id'], errors='coerce').astype('Int64')
    df = df.dropna(subset=['id']).reset_index(drop=True)

    # Covariates (cols 6-10 in 0-indexed: gender, age-group, freq, distance, purpose)
    # Column names contain zero-width spaces; use positional references
    col_names = list(df.columns)
    cov_rename = {
        col_names[6]: 'cov_gender',        # 性别 (1=male, 2=female)
        col_names[7]: 'cov_age_group',     # 年龄 (coded 1-6)
        col_names[8]: 'cov_visit_freq',    # 使用频率 (visit frequency per week)
        col_names[9]: 'cov_distance',      # 距离 (distance to green space)
        col_names[10]: 'cov_purpose',      # 目的 (primary purpose)
    }
    df = df.rename(columns=cov_rename)
    cov_cols = list(cov_rename.values())

    # Drop metadata columns not needed (timestamp, source, IP, duration)
    # Only keep id, covariates, and item columns
    item_chinese_cols = list(ITEM_MAP.keys())
    keep_cols = ['id'] + cov_cols + item_chinese_cols
    df = df[keep_cols]

    # Rename Chinese item columns to item_01..item_25
    df = df.rename(columns=ITEM_MAP)
    item_cols = list(ITEM_MAP.values())

    # Melt to long format
    long = df.melt(
        id_vars=['id'] + cov_cols,
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )

    # Clean responses
    long['resp'] = pd.to_numeric(long['resp'], errors='coerce')
    long = long.dropna(subset=['resp']).reset_index(drop=True)

    # Filter to valid 1-5 range
    long = long[(long['resp'] >= 1) & (long['resp'] <= 5)].reset_index(drop=True)

    # Enforce column order
    long = long[['id', 'item', 'resp'] + cov_cols]

    out_name = 'wang_2025_green_space_wellbeing.csv'
    out_path = os.path.join(OUT_DIR, out_name)
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
