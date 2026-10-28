# Section: Lines 25,000–28,522 — Edge Definitions (Second Half) & File Closure

## Overview

This final section of the file (~3,522 lines) contains a **dense mixture of interleaved node definitions and edge definitions**. Unlike a clean "edges-only" trailing section, the BotGhost visual builder serialized remaining late-added nodes inline with their connecting edges. This section contains:

- **92 edge objects** defining flow connections
- **59 node objects** (action nodes, condition nodes, conditionChild/else nodes) interleaved among edges
- The **JSON array closing bracket `]`** on the final line (28,522)
- The **root entry point edge** (`root` → `condition_5_d183_5a31`) — the command's top-level flow start
- Several critical subsystems: **ticket creation error handling**, **welcome message routing**, **pinned message metadata chain**, **ad injection (premium/chance)**, **support ping conditional**, **emoji initialization**, **transcript settings chain**, and the **"running" concurrency guard**

No edges in this range contain a `data` field with `conditionChild` references — all conditional routing is accomplished via `step`-type edges connecting conditions to their child branches, and `custom`-type edges connecting condition children to downstream actions.

---

## Edge Catalog

All 92 edges are documented below, organized by functional grouping.

---

### Group 1: Component Step Edges (Internal Node Wiring)

These `step`-type edges connect an action node to its internal component sub-node.

| # | Edge ID | Source | Target | Type | Handle |
|---|---------|--------|--------|------|--------|
| 1 | `edge_1725289429818_d338_ca21` | `action_1725289429818_453b_45be` | `action_1725289429818_5dc4_8dac` | step | sourceHandle: `components_source` |

---

### Group 2: Ticket Creation – Conditional Branch Outputs (conChild → Actions)

Edges from condition children that route to ticket-related action nodes (logging, DM, transcript messages).

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 2 | `edge_1725289429818_5497_a8bf` | `action_1725289429818_5dc4_8dac` | `action_1725289429818_a456_e4f3` | custom |
| 3 | `reactflow__edge-conChild_..._7dff_1516_3dd3action-action_1725289559692action` | `conChild_1723473744553_7dff_1516_3dd3` | `action_1725289559692` | custom |
| 4 | `reactflow__edge-conChild_..._1b7b_d701_3dd3action-action_1725289609209action` | `conChild_1723473744556_1b7b_d701_3dd3` | `action_1725289609209` | custom |
| 5 | `reactflow__edge-conChild_..._8db2_5fbe_3dd3action-action_1725289685658action` | `conChild_1723473744555_8db2_5fbe_3dd3` | `action_1725289685658` | custom |

**Functional meaning:**
- Edge 3: Routes condition child → **Ticket Created logging message** (sent to `{module_setting.panel.{index}.logging}` channel)
- Edge 4: Routes condition child → **Ticket Created DM** to user ("Your ticket has been created successfully")
- Edge 5: Routes condition child → **Ping to transcript channel** (sends `{ping}` to `{transcript_channel}`)

---

### Group 3: Transcript Channel Flow

Edges connecting the transcript-related message sending and condition checking.

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 6 | `reactflow__edge-action_1725289685658action-condition_..._8ad9_3e9b_3dd3action` | `action_1725289685658` | `condition_1723473744555_8ad9_3e9b_3dd3` | custom |
| 7 | `reactflow__edge-action_..._726c_a6be_3dd3action-action_1725289724607action` | `action_1723473744555_726c_a6be_3dd3` | `action_1725289724607` | custom |
| 8 | `reactflow__edge-action_1725289724607action-action_..._d90b_2324_3dd3action` | `action_1725289724607` | `action_1723473744553_d90b_2324_3dd3` | custom |
| 9 | `reactflow__edge-action_..._a437_2718_3dd3action-action_1725289724607action` | `action_1723473744555_a437_2718_3dd3` | `action_1725289724607` | custom |

**Functional meaning:**
- Edge 6: After ping → check transcript condition
- Edge 7: Action → **"Ticket Created - By {user_name}"** embed sent to transcript channel
- Edge 8: Transcript embed → continue to next action `action_..._d90b_2324_3dd3`
- Edge 9: **Convergent edge** — a second path also feeds into the transcript embed node `action_1725289724607` (merge point)

---

### Group 4: Error Handling — "Cannot Create Ticket" (Two Parallel Error Paths)

Two duplicated error-handling chains reset the `running` variable to `0` and display error messages.

#### Error Path A (via `else_..._53b1_b06b_3dd3`):

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 12 | `reactflow__edge-else_..._53b1_b06b_3dd3action-action_1725290406400_bcb1_5cc7action` | `else_1723473744555_53b1_b06b_3dd3` | `action_1725290406400_bcb1_5cc7` | custom |
| 10 | `edge_1725290406400_7885_0cd1` | `action_1725290406400_bcb1_5cc7` | `action_1725290406400_97ee_7e73` | custom |
| 13 | `reactflow__edge-action_1725290406400_97ee_7e73action-action_1725289180197action` | `action_1725290406400_97ee_7e73` | `action_1725289180197` | custom |

**Flow:** `else` → Set `running=0` → Send "Cannot Create Ticket" error → continue to `action_1725289180197`

#### Error Path B (via `else_..._e1b8_5c0e_3dd3`):

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 15 | `reactflow__edge-else_..._e1b8_5c0e_3dd3action-action_1725290406832_46aa_685daction` | `else_1723473744555_e1b8_5c0e_3dd3` | `action_1725290406832_46aa_685d` | custom |
| 11 | `edge_1725290406832_61a6_8331` | `action_1725290406832_46aa_685d` | `action_1725290406832_e449_fb12` | custom |
| 16 | `reactflow__edge-action_1725290406832_e449_fb12action-action_1725289429818_453b_45beaction` | `action_1725290406832_e449_fb12` | `action_1725289429818_453b_45be` | custom |

**Flow:** `else` → Set `running=0` → Send "Cannot Create Ticket" error → continue to `action_1725289429818_453b_45be`

---

### Group 5: Condition Branch Routing — `conChild_..._8bf3_ac85` → Support Ping Check

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 14 | `reactflow__edge-conChild_..._8bf3_ac85_3dd3action-action_..._bcc5_2ff2_3dd3action` | `conChild_1723473744555_8bf3_ac85_3dd3` | `action_1723473744553_bcc5_2ff2_3dd3` | custom |

Routes a condition child to a downstream action that then feeds into the **ping_supp** condition (Group 13).

---

### Group 6: Else Branch — Form/DM Path

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 17 | `reactflow__edge-$else_1306_5a6a_9794action-action_1724778380978action` | `$else_1306_5a6a_9794` | `action_1724778380978` | custom |
| 18 | `reactflow__edge-action_1724778380978action-action_..._c450_be46_3dd3action` | `action_1724778380978` | `action_1723473744556_c450_be46_3dd3` | custom |

**Flow:** `$else_1306` (else branch of a condition) → `action_1724778380978` → `action_..._c450_be46_3dd3`

---

### Group 7: Welcome Message Routing (Plain vs Embed)

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 52 | `reactflow__edge-action_1316_e3b3_0787action-action_1725290794777action` | `action_1316_e3b3_0787` | `action_1725290794777` | custom |
| 19 | `reactflow__edge-action_1725290794777action-action_..._f766_ce5a_3dd3action` | `action_1725290794777` | `action_1723473744553_f766_ce5a_3dd3` | custom |
| 53 | `reactflow__edge-action_1724779955279action-action_1725290909631action` | `action_1724779955279` | `action_1725290909631` | custom |
| 20 | `reactflow__edge-action_1725290909631action-action_1724779935218action` | `action_1725290909631` | `action_1724779935218` | custom |

**Flow:**
- **Plain welcome path:** `action_1316...` → `action_1725290794777` (PLAIN WELCOME: plain text content with `{ad}`) → `action_..._f766_ce5a`
- **Embed welcome path:** `action_1724779955279` → `action_1725290909631` (EMBED WELCOME: rich embed with panel settings) → `action_1724779935218`

---

### Group 8: Pinned Message Metadata Chain (8-Node Linear Chain)

A long sequential chain that sets all pinned message metadata variables into `bg_tickets_settings`.

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 35 | `reactflow__edge-action_1724779905373action-action_1725394324949action` | `action_1724779905373` | `action_1725394324949` | custom |
| 36 | `reactflow__edge-action_1725394324949action-action_1725291075778action` | `action_1725394324949` | `action_1725291075778` | custom |
| 21 | `reactflow__edge-action_1725291075778action-action_1725291124482action` | `action_1725291075778` | `action_1725291124482` | custom |
| 28 | `reactflow__edge-action_1725291124482action-action_1725291133919action` | `action_1725291124482` | `action_1725291133919` | custom |
| 27 | `reactflow__edge-action_1725291133919action-action_1725291147556action` | `action_1725291133919` | `action_1725291147556` | custom |
| 26 | `reactflow__edge-action_1725291147556action-action_1725291161051action` | `action_1725291147556` | `action_1725291161051` | custom |
| 25 | `reactflow__edge-action_1725291161051action-action_1725291174942action` | `action_1725291161051` | `action_1725291174942` | custom |
| 24 | `reactflow__edge-action_1725291174942action-action_1725291186638action` | `action_1725291174942` | `action_1725291186638` | custom |
| 23 | `reactflow__edge-action_1725291186638action-action_1725291349002action` | `action_1725291186638` | `action_1725291349002` | custom |
| 22 | `reactflow__edge-action_1725291349002action-action_1724779955279action` | `action_1725291349002` | `action_1724779955279` | custom |

**Full chain sequence (10 nodes):**
```
action_1724779905373
  → action_1725394324949 (set pinned_text = "<@{user_id}> {ping_plain}")
    → action_1725291075778 (set pinned_description)
      → action_1725291124482 (set pinned_title)
        → action_1725291133919 (set pinned_color)
          → action_1725291147556 (set pinned_author)
            → action_1725291161051 (set pinned_link)
              → action_1725291174942 (set pinned_thumbnail)
                → action_1725291186638 (set pinned_image)
                  → action_1725291349002 (set pinned_footer)
                    → action_1724779955279
```

All use `operation: "unshift"` on `bg_tickets_settings` with the ticket channel as target.

---

### Group 9: Form Data Storage & Routing

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 37 | `reactflow__edge-action_..._d56e_3671_3dd3action-action_1725394647947action` | `action_1723473744556_d56e_3671_3dd3` | `action_1725394647947` | custom |
| 38 | `reactflow__edge-action_1725394647947action-action_..._ff34_3bce_3dd3action` | `action_1725394647947` | `action_1723473744556_ff34_3bce_3dd3` | custom |

**Flow:** Action → Set `bg_tickets_settings.form = {form}` (unshift to ticket channel) → Continue

---

### Group 10: Miscellaneous Cross-System Routing

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 29 | `reactflow__edge-conChild155_026caction-action_1725284048895action` | `conChild155_026c` | `action_1725284048895` | custom |
| 30 | `reactflow__edge-action_1725285743982action-action_1725283423513action` | `action_1725285743982` | `action_1725283423513` | custom |
| 31 | `reactflow__edge-action_1725283423513action-condition_1339_1c20_8b8faction` | `action_1725283423513` | `condition_1339_1c20_8b8f` | custom |
| 32 | `reactflow__edge-action_1725283820267action-condition_151_058c_94afaction` | `action_1725283820267` | `condition_151_058c_94af` | custom |
| 33 | `reactflow__edge-action_1725283828916action-condition_151_058c_94afaction` | `action_1725283828916` | `condition_151_058c_94af` | custom |
| 39 | `reactflow__edge-action_401_561a_6e64action-condition_1719752096433_bd3d_ba91action` | `action_401_561a_6e64` | `condition_1719752096433_bd3d_ba91` | custom |

**Notes:**
- Edge 32 and 33 are **convergent edges**: two different actions both feed into the same condition `condition_151_058c_94af`
- Edge 31: Linear chain into a condition check
- Edge 39: Routes action output to a separate condition subsystem

---

### Group 11: Loop After → Condition & Root Entry Point

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 34 | `reactflow__edge-loop_after1388_e509_d340action-condition_1382_de06_bfceaction` | `loop_after1388_e509_d340` | `condition_1382_de06_bfce` | custom |
| 40 | `reactflow__edge-action_1725287539647_df4b_0417action-condition_1382_de06_bfceaction` | `action_1725287539647_df4b_0417` | `condition_1382_de06_bfce` | custom |
| **41** | **`reactflow__edge-rootaction-condition_5_d183_5a31action`** | **`root`** | **`condition_5_d183_5a31`** | **custom** |

**Critical edges:**
- **Edge 41 is the ROOT ENTRY POINT** — the very first edge of the entire command flow: `root` → `condition_5_d183_5a31`
- Edge 34: After a loop completes → re-evaluate condition `condition_1382_de06_bfce`
- Edge 40: Secondary entry into the same condition (convergent)

---

### Group 12: Emoji Initialization & Emoji Check Condition

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 42 | `reactflow__edge-conChild_1725285032500_66ee_e3bfaction-action_1725739969488action` | `conChild_1725285032500_66ee_e3bf` | `action_1725739969488` | custom |
| 47 | `reactflow__edge-$else_1382_a2e1_1537action-condition_1091_34db_076eaction` | `$else_1382_a2e1_1537` | `condition_1091_34db_076e` | custom |
| 46 | `reactflow__edge-condition_1091_34db_076e-$else_1091_e9e0_689e` | `condition_1091_34db_076e` | `$else_1091_e9e0_689e` | step |
| 48 | `reactflow__edge-condition_1091_34db_076e-conChild1094_1f04` | `condition_1091_34db_076e` | `conChild1094_1f04` | step |
| 49 | `reactflow__edge-conChild1094_1f04action-action_1096_4e98_65baaction` | `conChild1094_1f04` | `action_1096_4e98_65ba` | custom |
| 50 | `reactflow__edge-action_1096_4e98_65baaction-action_1337_e4d4_0c87action` | `action_1096_4e98_65ba` | `action_1337_e4d4_0c87` | custom |
| 51 | `reactflow__edge-$else_1091_e9e0_689eaction-action_1337_e4d4_0c87action` | `$else_1091_e9e0_689e` | `action_1337_e4d4_0c87` | custom |

**Flow:**
```
$else_1382_a2e1_1537  →  condition_1091_34db_076e (check {emojis})
                             ├── conChild1094_1f04 (emojis == "")
                             │     → action_1096_4e98_65ba (set emojis = ",,,,,,,,,,,,,,,,,,,,,,,," — 24 commas)
                             │       → action_1337_e4d4_0c87
                             └── $else_1091_e9e0_689e (emojis not empty)
                                   → action_1337_e4d4_0c87  (convergent)
```

Both branches converge to `action_1337_e4d4_0c87`.

---

### Group 13: Ticket Variable Setup (ticket, ticket_name) → Edit Message

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 43 | `reactflow__edge-action_..._ab9a_a265_3dd3action-action_1725740510445action` | `action_1723473744553_ab9a_a265_3dd3` | `action_1725740510445` | custom |
| 44 | `reactflow__edge-action_1725740510445action-action_1725740537704action` | `action_1725740510445` | `action_1725740537704` | custom |
| 45 | `reactflow__edge-action_1725740537704action-action_1725290306594action` | `action_1725740537704` | `action_1725290306594` | custom |

**Flow:**
```
action_..._ab9a_a265 → Set ticket = "<#{ticket_id}>"
                      → Set ticket_name = "{channel_name[{ticket_id}]}"
                        → action_1725290306594 (Send "Ticket Created" edit message)
```

---

### Group 14: Support Ping Conditional (`ping_supp` Check)

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 55 | `reactflow__edge-action_..._bcc5_2ff2_3dd3action-condition_1093_fe1c_1e30action` | `action_1723473744553_bcc5_2ff2_3dd3` | `condition_1093_fe1c_1e30` | custom |
| 54 | `reactflow__edge-condition_1093_fe1c_1e30-$else_1093_26e4_f6b1` | `condition_1093_fe1c_1e30` | `$else_1093_26e4_f6b1` | step |
| 56 | `reactflow__edge-condition_1093_fe1c_1e30-conChild1097_a1fa` | `condition_1093_fe1c_1e30` | `conChild1097_a1fa` | step |
| 57 | `reactflow__edge-$else_1093_26e4_f6b1action-action_1099_2fc4_6255action` | `$else_1093_26e4_f6b1` | `action_1099_2fc4_6255` | custom |
| 58 | `reactflow__edge-action_1099_2fc4_6255action-action_..._fbe9_cbc2_3dd3action` | `action_1099_2fc4_6255` | `action_1723473744553_fbe9_cbc2_3dd3` | custom |
| 60 | `reactflow__edge-conChild1097_a1faaction-action_1727463042593action` | `conChild1097_a1fa` | `action_1727463042593` | custom |
| 59 | `reactflow__edge-action_1727463042593action-action_..._fbe9_cbc2_3dd3action` | `action_1727463042593` | `action_1723473744553_fbe9_cbc2_3dd3` | custom |

**Flow:**
```
action_..._bcc5_2ff2 → condition_1093_fe1c_1e30 (check {module_setting.panel.{index}.ping_supp})
                          ├── conChild1097_a1fa (ping_supp == "true")
                          │     → action_1727463042593 (set ping_plain = "{ping}")
                          │       → action_..._fbe9_cbc2  (convergent)
                          └── $else_1093_26e4_f6b1 (ping_supp != "true")
                                → action_1099_2fc4_6255 (set ping_plain = "")
                                  → action_..._fbe9_cbc2  (convergent)
```

Both branches converge to `action_1723473744553_fbe9_cbc2_3dd3`.

---

### Group 15: Secondary Ping Plain Assignment

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 62 | `reactflow__edge-action_..._ccbb_3f58_3dd3action-action_1727463067654action` | `action_1723473744553_ccbb_3f58_3dd3` | `action_1727463067654` | custom |
| 61 | `reactflow__edge-action_1727463067654action-action_..._a69c_bac1_3dd3action` | `action_1727463067654` | `action_1723473744553_a69c_bac1_3dd3` | custom |

**Flow:** `action_..._ccbb_3f58` → Set `ping_plain = "{ping}"` → `action_..._a69c_bac1`

This is a separate path (not behind a condition) that unconditionally sets `ping_plain` to `{ping}`.

---

### Group 16: Premium Check → "Running" Concurrency Guard

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 69 | `reactflow__edge-action_1723467885832_e33c_2c14_1cbaaction-condition_1116_1d39_70fdaction` | `action_1723467885832_e33c_2c14_1cba` | `condition_1116_1d39_70fd` | custom |
| 67 | `reactflow__edge-condition_1116_1d39_70fd-$else_1116_3abd_30b7` | `condition_1116_1d39_70fd` | `$else_1116_3abd_30b7` | step |
| 68 | `reactflow__edge-condition_1116_1d39_70fd-conChild1119_tca5p5lyo` | `condition_1116_1d39_70fd` | `conChild1119_tca5p5lyo` | step |
| 70 | `reactflow__edge-$else_1116_3abd_30b7action-condition_1730746585092_0e78_2fb5action` | `$else_1116_3abd_30b7` | `condition_1730746585092_0e78_2fb5` | custom |
| 63 | `edge_1730746585092_a8c7_3c80` | `condition_1730746585092_0e78_2fb5` | `else_1730746585091_ca4d_896f` | step |
| 64 | `edge_1730746585092_5f75_924b` | `condition_1730746585092_0e78_2fb5` | `conChild_1730746585092_760a_e18d` | step |
| 65 | `edge_1730746585092_50d3_0bb8` | `conChild_1730746585092_760a_e18d` | `action_1730746585092_82d4_6de1` | custom |
| 66 | `edge_1730746585092_e26e_ee23` | `action_1730746585092_82d4_6de1` | `action_1730746585092_9803_2cd3` | custom |
| 71 | `reactflow__edge-action_1730746585092_9803_2cd3action-condition_1723467885833_b8ce_8be9_1cbaaction` | `action_1730746585092_9803_2cd3` | `condition_1723467885833_b8ce_8be9_1cba` | custom |
| 72 | `reactflow__edge-conChild1119_tca5p5lyoaction-condition_1723467885833_b8ce_8be9_1cbaaction` | `conChild1119_tca5p5lyo` | `condition_1723467885833_b8ce_8be9_1cba` | custom |

**Flow:**
```
action_..._e33c_2c14 → condition_1116_1d39_70fd (Premium Check)
                          ├── conChild1119_tca5p5lyo (IS premium)
                          │     → condition_1723467885833_b8ce_8be9_1cba  (skip wait, go direct)
                          └── $else_1116_3abd_30b7 (NOT premium)
                                → condition_1730746585092_0e78_2fb5 (check {running})
                                    ├── conChild_..._760a_e18d (running == "1")
                                    │     → action_..._82d4_6de1 (Send "ticket being created, please wait...")
                                    │       → action_..._9803_2cd3 (Wait 8 seconds)
                                    │         → condition_1723467885833_b8ce_8be9_1cba
                                    └── else_..._ca4d_896f (running != "1")
                                          [continues elsewhere]
```

**Purpose:** Non-premium users who hit a concurrency condition (`running == 1`) get a "please wait" message and an 8-second delay before proceeding. Premium users skip this entirely.

---

### Group 17: Premium Check → Ad Injection (Chance-Based)

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 82 | `reactflow__edge-action_1725290306594action-condition_1134_f603_24c2action` | `action_1725290306594` | `condition_1134_f603_24c2` | custom |
| 79 | `reactflow__edge-condition_1134_f603_24c2-$else_1134_8150_39c9` | `condition_1134_f603_24c2` | `$else_1134_8150_39c9` | step |
| 80 | `reactflow__edge-condition_1134_f603_24c2-conChild1137_z0d241vx8` | `condition_1134_f603_24c2` | `conChild1137_z0d241vx8` | step |
| 81 | `reactflow__edge-$else_1134_8150_39c9action-condition_1123_39a2_71a3action` | `$else_1134_8150_39c9` | `condition_1123_39a2_71a3` | custom |
| 83 | `reactflow__edge-conChild1137_z0d241vx8action-action_1128_dec4_b598action` | `conChild1137_z0d241vx8` | `action_1128_dec4_b598` | custom |
| 73 | `reactflow__edge-condition_1123_39a2_71a3-$else_1123_e458_7134` | `condition_1123_39a2_71a3` | `$else_1123_e458_7134` | step |
| 74 | `reactflow__edge-condition_1123_39a2_71a3-conChild1126_x7qdu4pu8` | `condition_1123_39a2_71a3` | `conChild1126_x7qdu4pu8` | step |
| 75 | `reactflow__edge-conChild1126_x7qdu4pu8action-action_1730750464511action` | `conChild1126_x7qdu4pu8` | `action_1730750464511` | custom |
| 76 | `reactflow__edge-$else_1123_e458_7134action-action_1128_dec4_b598action` | `$else_1123_e458_7134` | `action_1128_dec4_b598` | custom |
| 77 | `reactflow__edge-action_1128_dec4_b598action-condition_1306_bd17_61bfaction` | `action_1128_dec4_b598` | `condition_1306_bd17_61bf` | custom |
| 78 | `reactflow__edge-action_1730750464511action-condition_1306_bd17_61bfaction` | `action_1730750464511` | `condition_1306_bd17_61bf` | custom |

**Flow:**
```
action_1725290306594 ("Ticket Created" edit)
  → condition_1134_f603_24c2 (Premium Check #2)
      ├── conChild1137_z0d241vx8 (IS premium)
      │     → action_1128_dec4_b598 (set ad = "")  → condition_1306_bd17_61bf
      └── $else_1134_8150_39c9 (NOT premium)
            → condition_1123_39a2_71a3 (Chance Condition)
                ├── conChild1126_x7qdu4pu8 (35% chance)
                │     → action_1730750464511 (set ad = BotGhost welcome ad text)
                │       → condition_1306_bd17_61bf  (convergent)
                └── $else_1123_e458_7134 (65% chance — no ad)
                      → action_1128_dec4_b598 (set ad = "")
                        → condition_1306_bd17_61bf  (convergent)
```

**Purpose:** Premium bots never show ads. Non-premium bots have a 35% chance of showing a BotGhost advertisement in the ticket welcome message. All paths converge to `condition_1306_bd17_61bf`.

---

### Group 18: Transcript Mode Conditional & Settings Chain

| # | Edge ID | Source | Target | Type |
|---|---------|--------|--------|------|
| 91 | `reactflow__edge-action_..._e166_164c_3dd3action-condition_1141_9b53_f2b7action` | `action_1723473744553_e166_164c_3dd3` | `condition_1141_9b53_f2b7` | custom |
| 84 | `reactflow__edge-condition_1141_9b53_f2b7-$else_1141_600f_57e1` | `condition_1141_9b53_f2b7` | `$else_1141_600f_57e1` | step |
| 85 | `reactflow__edge-condition_1141_9b53_f2b7-conChild1144_32b6` | `condition_1141_9b53_f2b7` | `conChild1144_32b6` | step |
| 86 | `reactflow__edge-$else_1141_600f_57e1action-action_..._9158_abf7_3dd3action` | `$else_1141_600f_57e1` | `action_1723473744553_9158_abf7_3dd3` | custom |
| 87 | `reactflow__edge-conChild1144_32b6action-action_1767714696304action` | `conChild1144_32b6` | `action_1767714696304` | custom |
| 88 | `reactflow__edge-action_1767714696304action-action_1767714712907action` | `action_1767714696304` | `action_1767714712907` | custom |
| 89 | `reactflow__edge-action_1767714712907action-action_1767714775652action` | `action_1767714712907` | `action_1767714775652` | custom |
| 90 | `reactflow__edge-action_1767714775652action-action_1767714790132action` | `action_1767714775652` | `action_1767714790132` | custom |
| 92 | `reactflow__edge-action_1767714790132action-action_1767715045103action` | `action_1767714790132` | `action_1767715045103` | custom |

**Flow:**
```
action_..._e166_164c → condition_1141_9b53_f2b7 (check {module_setting.transcript.{transcript_id}.t_mode})
                          ├── conChild1144_32b6 (t_mode == "web")
                          │     → action_1767714696304 (set transcript_enabled = "web")
                          │       → action_1767714712907 (set transcript_theme)
                          │         → action_1767714775652 (set transcript_view)
                          │           → action_1767714790132 (set transcript_password)
                          │             → action_1767715045103 (set tr_id = "")
                          └── $else_1141_600f_57e1 (t_mode != "web")
                                → action_..._9158_abf7_3dd3
```

**Purpose:** When transcript mode is "web", stores all transcript-related settings (theme, view, password) into `bg_tickets_settings` for the ticket channel. Non-web modes skip to a different action.

---

## Conditional Edges

### Condition → Branch Step Edges (12 total)

These `step`-type edges connect condition nodes to their child branches. They have **no sourceHandle/targetHandle** and represent the condition's internal branching structure.

| # | Condition Source | Target Branch | Edge ID |
|---|-----------------|---------------|---------|
| 1 | `condition_1091_34db_076e` | `$else_1091_e9e0_689e` | `reactflow__edge-condition_1091_34db_076e-$else_1091_e9e0_689e` |
| 2 | `condition_1091_34db_076e` | `conChild1094_1f04` | `reactflow__edge-condition_1091_34db_076e-conChild1094_1f04` |
| 3 | `condition_1093_fe1c_1e30` | `$else_1093_26e4_f6b1` | `reactflow__edge-condition_1093_fe1c_1e30-$else_1093_26e4_f6b1` |
| 4 | `condition_1093_fe1c_1e30` | `conChild1097_a1fa` | `reactflow__edge-condition_1093_fe1c_1e30-conChild1097_a1fa` |
| 5 | `condition_1116_1d39_70fd` | `$else_1116_3abd_30b7` | `reactflow__edge-condition_1116_1d39_70fd-$else_1116_3abd_30b7` |
| 6 | `condition_1116_1d39_70fd` | `conChild1119_tca5p5lyo` | `reactflow__edge-condition_1116_1d39_70fd-conChild1119_tca5p5lyo` |
| 7 | `condition_1123_39a2_71a3` | `$else_1123_e458_7134` | `reactflow__edge-condition_1123_39a2_71a3-$else_1123_e458_7134` |
| 8 | `condition_1123_39a2_71a3` | `conChild1126_x7qdu4pu8` | `reactflow__edge-condition_1123_39a2_71a3-conChild1126_x7qdu4pu8` |
| 9 | `condition_1134_f603_24c2` | `$else_1134_8150_39c9` | `reactflow__edge-condition_1134_f603_24c2-$else_1134_8150_39c9` |
| 10 | `condition_1134_f603_24c2` | `conChild1137_z0d241vx8` | `reactflow__edge-condition_1134_f603_24c2-conChild1137_z0d241vx8` |
| 11 | `condition_1141_9b53_f2b7` | `$else_1141_600f_57e1` | `reactflow__edge-condition_1141_9b53_f2b7-$else_1141_600f_57e1` |
| 12 | `condition_1141_9b53_f2b7` | `conChild1144_32b6` | `reactflow__edge-condition_1141_9b53_f2b7-conChild1144_32b6` |

Plus the `condition_1730746585092_0e78_2fb5` condition has 2 step edges:
| 13 | `condition_1730746585092_0e78_2fb5` | `else_1730746585091_ca4d_896f` | `edge_1730746585092_a8c7_3c80` |
| 14 | `condition_1730746585092_0e78_2fb5` | `conChild_1730746585092_760a_e18d` | `edge_1730746585092_5f75_924b` |

### Edges with `data` Fields

**None.** No edges in this range contain `data.conditionChild` fields. All conditional routing uses the `step` edge type from condition nodes to child branches, and `custom` edges from child branches to downstream actions.

---

## Flow Patterns

### Pattern 1: Condition → Branch → Convergence
The dominant pattern. A condition node splits into 2+ branches via `step` edges, each branch executes its actions, and both converge to a common downstream node.

**Instances:**
- Emoji check (`condition_1091`): both branches → `action_1337_e4d4_0c87`
- Ping support check (`condition_1093`): both branches → `action_..._fbe9_cbc2`
- Premium check #1 (`condition_1116`): both branches → `condition_1723467885833_b8ce_8be9_1cba`
- Chance condition (`condition_1123`) + Premium check #2 (`condition_1134`): all paths → `condition_1306_bd17_61bf`
- Running check (`condition_1730746585092`): running=1 path → wait → same target as premium path
- Transcript mode (`condition_1141`): web path runs settings chain; non-web goes elsewhere

### Pattern 2: Long Sequential Chains
Multiple action nodes connected in strict linear order with `action→action` custom edges.

**Instance:** Pinned metadata chain — 10 sequential nodes setting `bg_tickets_settings` keys (text → description → title → color → author → link → thumbnail → image → footer → next action)

**Instance:** Transcript settings chain — 5 sequential nodes (transcript_enabled → transcript_theme → transcript_view → transcript_password → tr_id)

### Pattern 3: Multi-Input Convergence
Multiple source nodes connecting to a single target node.

**Instances:**
- `condition_151_058c_94af` receives from both `action_1725283820267` and `action_1725283828916`
- `condition_1382_de06_bfce` receives from both `loop_after1388_e509_d340` and `action_1725287539647_df4b_0417`
- `action_1725289724607` receives from both `action_..._726c_a6be` and `action_..._a437_2718`
- `action_1337_e4d4_0c87` receives from both `action_1096_4e98_65ba` and `$else_1091_e9e0_689e`
- `action_..._fbe9_cbc2` receives from both `action_1099_2fc4_6255` and `action_1727463042593`
- `condition_1306_bd17_61bf` receives from both `action_1128_dec4_b598` and `action_1730750464511`

### Pattern 4: Duplicated Error Handling Paths
Two nearly identical error chains (set `running=0` → send "Cannot Create Ticket") exist for different else branches, each terminating at different downstream nodes. This appears to be two context-specific error handlers for different ticket creation failure scenarios.

### Pattern 5: Premium Gating
Premium check conditions appear twice, acting as feature gates:
1. **Concurrency guard skip** (Group 16): Premium users bypass the 8-second wait
2. **Ad injection skip** (Group 17): Premium users never see BotGhost ads

### Pattern 6: Root Entry
The `root → condition_5_d183_5a31` edge (Edge 41) defines the command's entry point. This is the single starting edge for the entire command graph.

---

## File Termination

The file ends at **line 28,522** with:

```json
    {
        "source": "action_1767714790132",
        "sourceHandle": "action",
        "target": "action_1767715045103",
        "targetHandle": "action",
        "animated": false,
        "arrowHeadType": "arrowclosed",
        "type": "custom",
        "id": "reactflow__edge-action_1767714790132action-action_1767715045103action"
    }
]
```

- The **last element** in the top-level JSON array is edge `reactflow__edge-action_1767714790132action-action_1767715045103action` (transcript password → tr_id initialization)
- The array is **closed with `]`** on line 28,522
- There is **no trailing comma** after the last object (valid JSON)
- There is **no wrapping object** — the entire file is a flat JSON array `[...]`
- The last node defined is `action_1767715045103` (Set unique variable `tr_id = ""`), marked `"selected": true` — the only selected element in this range

---

## Interleaved Nodes in This Range

59 nodes appear interleaved with edges in this section. Full catalog:

### Action Nodes (31)

| Node ID | Type | Function | Key Data |
|---------|------|----------|----------|
| `action_1725289559692` | advanced_message | Ticket Created logging | Target: `{module_setting.panel.{index}.logging}` |
| `action_1725289609209` | advanced_message | Ticket Created DM | Target: DM to command user |
| `action_1725289685658` | advanced_message | Ping transcript | Content: `{ping}`, target: `{transcript_channel}` |
| `action_1725289724607` | advanced_message | Transcript embed | Author: "Ticket Created - By {user_name}" |
| `action_1725290306594` | advanced_message | Edit: Ticket Created | EditId: `1725290362504_40756` |
| `action_1725290406400_bcb1_5cc7` | set_unique_variable | Reset running | `running = 0` |
| `action_1725290406400_97ee_7e73` | advanced_message | Error: Cannot Create | EditId: `1725290362504_40756` |
| `action_1725290406832_46aa_685d` | set_unique_variable | Reset running | `running = 0` |
| `action_1725290406832_e449_fb12` | advanced_message | Error: Cannot Create | EditId: `1725290362504_40756` |
| `action_1725290794777` | advanced_message | PLAIN WELCOME | Variable: `pinned`, content with `{ad}` |
| `action_1725290909631` | advanced_message | EMBED WELCOME | Variable: `pinned`, embed with panel settings |
| `action_1725291075778` | set_var | Set pinned_description | Unshift to `bg_tickets_settings` |
| `action_1725291124482` | set_var | Set pinned_title | Unshift to `bg_tickets_settings` |
| `action_1725291133919` | set_var | Set pinned_color | Unshift to `bg_tickets_settings` |
| `action_1725291147556` | set_var | Set pinned_author | Unshift to `bg_tickets_settings` |
| `action_1725291161051` | set_var | Set pinned_link | Unshift to `bg_tickets_settings` |
| `action_1725291174942` | set_var | Set pinned_thumbnail | Unshift to `bg_tickets_settings` |
| `action_1725291186638` | set_var | Set pinned_image | Unshift to `bg_tickets_settings` |
| `action_1725291349002` | set_var | Set pinned_footer | Unshift to `bg_tickets_settings` |
| `action_1725394324949` | set_var | Set pinned_text | `<@{user_id}> {ping_plain}` |
| `action_1725394647947` | set_var | Set form | `{form}` |
| `action_1725739969488` | set_unique_variable | Init emojis | `emojis = ""` |
| `action_1725740510445` | set_unique_variable | Set ticket ref | `ticket = <#{ticket_id}>` |
| `action_1725740537704` | set_unique_variable | Set ticket_name | `{channel_name[{ticket_id}]}` |
| `action_1096_4e98_65ba` | set_unique_variable | Set default emojis | `emojis = ",,,,,,,,,,,,,,,,,,,,,,,"` (24 commas) |
| `action_1099_2fc4_6255` | set_unique_variable | Clear ping_plain | `ping_plain = ""` |
| `action_1727463042593` | set_unique_variable | Set ping_plain | `ping_plain = "{ping}"` |
| `action_1727463067654` | set_unique_variable | Set ping_plain | `ping_plain = "{ping}"` |
| `action_1730746585092_9803_2cd3` | wait_action | Wait 8 seconds | Concurrency delay |
| `action_1730746585092_82d4_6de1` | advanced_message | "Please wait" msg | EditId: `1725290362504_40756` |
| `action_1128_dec4_b598` | set_unique_variable | Clear ad | `ad = ""` |
| `action_1730750464511` | set_unique_variable | Set ad | BotGhost advertisement text |
| `action_1767714696304` | set_var | Set transcript_enabled | `"web"` |
| `action_1767714712907` | set_var | Set transcript_theme | `{module_setting.transcript.{transcript_id}.t_theme}` |
| `action_1767714775652` | set_var | Set transcript_view | `{module_setting.transcript.{transcript_id}.t_view}` |
| `action_1767714790132` | set_var | Set transcript_password | `{module_setting.transcript.{transcript_id}.t_password}` |
| `action_1767715045103` | set_unique_variable | Init tr_id | `tr_id = ""` |

### Condition Nodes (6)

| Node ID | Condition Type | Base Value |
|---------|---------------|------------|
| `condition_1091_34db_076e` | comparison | `{emojis}` |
| `condition_1093_fe1c_1e30` | comparison | `{module_setting.panel.{index}.ping_supp}` |
| `condition_1116_1d39_70fd` | premium | (premium check) |
| `condition_1123_39a2_71a3` | chance | (percent chance) |
| `condition_1134_f603_24c2` | premium | (premium check) |
| `condition_1141_9b53_f2b7` | comparison | `{module_setting.transcript.{transcript_id}.t_mode}` |
| `condition_1730746585092_0e78_2fb5` | comparison | `{running}` |

### ConditionChild/Else Nodes (15)

| Node ID | Branch Type | Comparison Value |
|---------|-------------|-----------------|
| `$else_1091_e9e0_689e` | else | — |
| `conChild1094_1f04` | equal_to | `""` (empty string) |
| `$else_1093_26e4_f6b1` | else | — |
| `conChild1097_a1fa` | equal_to | `"true"` |
| `else_1730746585091_ca4d_896f` | else | — |
| `conChild_1730746585092_760a_e18d` | equal_to | `"1"` |
| `$else_1116_3abd_30b7` | else (premium) | — |
| `conChild1119_tca5p5lyo` | premium | — |
| `$else_1123_e458_7134` | else (chance) | — |
| `conChild1126_x7qdu4pu8` | chance | `"35"` (35%) |
| `$else_1134_8150_39c9` | else (premium) | — |
| `conChild1137_z0d241vx8` | premium | — |
| `$else_1141_600f_57e1` | else | — |
| `conChild1144_32b6` | equal_to | `"web"` |

---

## Edge Cases / Notes

1. **Root entry point appears late in the file** (Edge 41, ~line 26829): The `root → condition_5_d183_5a31` edge — the command's starting point — is serialized near the end of the file, not at the beginning. This confirms BotGhost serializes elements in creation/modification order, not execution order.

2. **Duplicate error handling chains**: Two nearly identical `running=0` + "Cannot Create Ticket" patterns exist (Error Path A and B), targeting different editIds but using the same `editId: 1725290362504_40756`. They differ only in their downstream targets (`action_1725289180197` vs `action_1725289429818_453b_45be`).

3. **The `selected: true` anomaly**: Node `action_1767715045103` (the very last node in the file) has `"selected": true`. All other nodes/edges have `"selected": false`. This indicates it was the last element the user had selected when the file was saved/exported.

4. **Timestamp-based IDs reveal creation timeline**:
   - `1723467885832` = earliest (Aug 12, 2024)
   - `1725290...` range = late Aug/early Sep 2024
   - `1727463042593` = Sep 27, 2024  
   - `1730746585092` = Nov 4, 2024
   - `1767714696304` = latest (Jun 6, 2025+)
   
   The transcript settings chain (Group 18) with IDs `1767714...` was the **most recently added feature**.

5. **35% ad injection for non-premium**: The `condition_1123_39a2_71a3` (Chance Condition) uses a 35% probability to inject a BotGhost advertisement into non-premium ticket welcome messages. Premium bots skip this entirely via `condition_1134_f603_24c2`.

6. **Emoji initialization with 24 commas**: `action_1096_4e98_65ba` sets the `emojis` variable to exactly 24 commas (`,,,,,,,,,,,,,,,,,,,,,,,,`). This is likely a delimiter-separated empty array used for emoji slot allocation in ticket panels.

7. **The `component_source` handle**: Edge 1 uses `sourceHandle: "components_source"` (unique in this range), indicating a node-internal wiring for UI component sub-elements (buttons/select menus).

8. **No `data` fields on edges**: Unlike some BotGhost exports where edges carry `data.conditionChild` references, **all edges in this range are data-free**. Conditional routing is entirely structural (condition → step edges → children).

9. **File structure is a flat JSON array**: The entire 28,522-line file is a single `[...]` array containing a mix of node objects and edge objects. There is no wrapping `{ "nodes": [...], "edges": [...] }` structure — nodes and edges are freely intermixed in creation order.

10. **Multiple paths into `condition_1382_de06_bfce`**: This condition receives flow from both `loop_after1388_e509_d340` (post-loop) and `action_1725287539647_df4b_0417`, indicating it serves as a re-entry point for loop iteration and initialization.
