-- Auto Defense — itens defensivos automáticos (qualquer herói)
-- Cura, barreira, cleanse e survive por HP, debuff e tecla pânico

local UNIT_METER = 37.7358490566
local ITEM_SLOT_FIRST = (EAbilitySlots_t and EAbilitySlots_t.ESlot_ActiveItem_First) or 4
local ITEM_INPUT_BY_IDX = {
    [1] = InputBitMask_t.IN_ITEM1,
    [2] = InputBitMask_t.IN_ITEM2,
    [3] = InputBitMask_t.IN_ITEM3,
    [4] = InputBitMask_t.IN_ITEM4,
}

local DEFENSE_KIND = {
    CLEANSE = 1,
    BARRIER = 2,
    HEAL    = 3,
    SURVIVE = 4,
}

local DEFENSE_ITEMS = {
    {
        id = "auto_cleanse", name = "Dispel Magic",
        patterns = { "upgrade_reduce_debuff_duration", "dispel magic", "debuff_remover", "debuff remover" },
        kind = DEFENSE_KIND.CLEANSE, order = 10, default_on = true,
        timing = "On CC received",
        desc = "Automatically removes debuffs when you are under control.",
    },
    {
        id = "divine_barrier", name = "Divine Barrier",
        patterns = { "divine barrier", "upgrade_divine_barrier", "divine_barrier" },
        kind = DEFENSE_KIND.BARRIER, order = 20, default_on = true,
        timing = "Low HP + pressure",
        desc = "Strong barrier — high defensive priority.",
    },
    {
        id = "guardian_ward", name = "Guardian Ward",
        patterns = { "guardian ward", "upgrade_guardian_ward", "guardian_ward" },
        kind = DEFENSE_KIND.BARRIER, order = 21, default_on = true,
        timing = "Low HP + pressure",
        desc = "Defensive shield/ward.",
    },
    {
        id = "vex_barrier", name = "Reactive Barrier",
        patterns = { "upgrade_vex_barrier", "reactive barrier", "vex_barrier" },
        kind = DEFENSE_KIND.BARRIER, order = 22, default_on = false,
        timing = "Low HP",
        desc = "Reactive barrier on damage taken.",
    },
    {
        id = "weapon_shielding", name = "Weapon Shielding",
        patterns = { "upgrade_weapon_shielding", "weapon shielding", "weapon_shielding" },
        kind = DEFENSE_KIND.BARRIER, order = 23, default_on = false,
        timing = "Low HP + pressure",
        desc = "Barrier when taking significant weapon damage.",
    },
    {
        id = "spirit_shielding", name = "Spirit Shielding",
        patterns = { "upgrade_spirit_bubble", "spirit shielding", "spirit_shielding" },
        kind = DEFENSE_KIND.BARRIER, order = 24, default_on = false,
        timing = "Low HP + pressure",
        desc = "Barrier when taking significant spirit damage.",
    },
    {
        id = "spellbreaker", name = "Spellbreaker",
        patterns = { "upgrade_spellbreaker", "spellbreaker" },
        kind = DEFENSE_KIND.BARRIER, order = 25, default_on = false,
        timing = "Low HP",
        desc = "Reduces the next high spirit damage hit.",
    },
    {
        id = "healing_rite", name = "Healing Rite",
        patterns = { "upgrade_personal_rejuvenator", "upgrade_health_stimpak", "healing rite", "healing_rite" },
        kind = DEFENSE_KIND.HEAL, order = 30, default_on = true,
        timing = "Critical HP",
        desc = "Regen and sprint speed — best for lane sustain.",
    },
    {
        id = "healing_nova", name = "Healing Nova",
        patterns = { "upgrade_health_nova", "healing nova", "health_nova" },
        kind = DEFENSE_KIND.HEAL, order = 31, default_on = false,
        timing = "Critical HP",
        desc = "Heal in area around you.",
    },
    {
        id = "radiant_regeneration", name = "Radiant Regeneration",
        patterns = { "upgrade_resonant_healing", "radiant regeneration", "resonant_healing" },
        kind = DEFENSE_KIND.HEAL, order = 32, default_on = false,
        timing = "Critical HP",
        desc = "Heal over time after casting abilities.",
    },
    {
        id = "arcane_surge", name = "Arcane Surge",
        patterns = { "arcane surge", "upgrade_arcane_surge", "arcane_surge" },
        kind = DEFENSE_KIND.SURVIVE, order = 40, default_on = false,
        timing = "Under focus",
        desc = "Spirit power + short sustain.",
    },
    {
        id = "unstoppable_def", name = "Unstoppable (Defense)",
        patterns = { "upgrade_unstoppable", "unstoppable" },
        kind = DEFENSE_KIND.SURVIVE, order = 41, default_on = false,
        timing = "Under focus / CC",
        desc = "Immune to interrupts — defensive when focused.",
    },
}

local DEFENSE_ORDERS = {
    { DEFENSE_KIND.CLEANSE, DEFENSE_KIND.BARRIER, DEFENSE_KIND.HEAL, DEFENSE_KIND.SURVIVE },
    { DEFENSE_KIND.BARRIER, DEFENSE_KIND.HEAL,   DEFENSE_KIND.CLEANSE, DEFENSE_KIND.SURVIVE },
    { DEFENSE_KIND.HEAL,    DEFENSE_KIND.BARRIER, DEFENSE_KIND.CLEANSE, DEFENSE_KIND.SURVIVE },
}

local DEBUFF_PATTERNS = {
    "stun", "silence", "sleep", "root", "disarm", "knock", "fear", "taunt", "hex", "curse", "suppress",
}

-- ─── Menu ───────────────────────────────────────────────────────────────────

-- 4 args = CThirdTab (com 3 args vira CSecondTab e :Create() retorna nil)
local defense_tab = Menu.Create("Miscellaneous", "Utility", "Auto Defense", "\u{f3ed} Auto Defense")
local root = defense_tab:Create("General")

local ui = {
    enable             = root:Switch("Enable Auto Defense", true, "\u{f3ed}"),
    show_hud           = root:Switch("Show HUD", true),
    hp_threshold       = root:Slider("HP Threshold %", 5, 95, 40, "%d%%"),
    require_threat     = root:Switch("Require Nearby Enemies", false),
    threat_radius_m    = root:Slider("Threat Radius (m)", 5.0, 40.0, 18.0, "%.0fm"),
    min_enemies        = root:Slider("Min Enemies Nearby", 1, 4, 1, "%d"),
    use_on_debuff      = root:Switch("Use Cleanse on Debuff", true),
    debuff_hp_max      = root:Slider("Cleanse Max HP %", 10, 100, 85, "%d%%"),
    allow_during_combo = root:Switch("Allow During Combo", false),
    panic_key          = root:Bind("Panic Key", Enum.ButtonCode.KEY_NONE),
    cooldown_ms        = root:Slider("Cast Cooldown (ms)", 200, 3000, 800, "%d ms"),
    item_hold_ms       = root:Slider("Item Hold (ms)", 30, 400, 80, "%d ms"),
    queue_order        = root:Combo("Priority Order", {
        "Cleanse → Barrier → Heal",
        "Barrier → Heal → Cleanse",
        "Heal → Barrier → Cleanse",
    }, 0),
}

ui.enable:ToolTip("Uses defensive items automatically when HP is low or under debuff.")
ui.hp_threshold:ToolTip("Max HP% to trigger heal/barrier.")
ui.require_threat:ToolTip("Requires nearby enemies in addition to HP threshold.")
ui.use_on_debuff:ToolTip("Uses cleanse even above HP threshold if under CC.")
ui.panic_key:ToolTip("Forces best available defensive item (ignores HP).")
ui.allow_during_combo:ToolTip("Allows defense during script combos (e.g. Paradox Combo).")

local ui_item = {}
for _, def in ipairs(DEFENSE_ITEMS) do
    local grp = defense_tab:Create(def.name)
    ui_item[def.id] = {
        use = grp:Switch("Use Auto Defense", def.default_on),
    }
    ui_item[def.id].use:ToolTip(def.desc)
    grp:Label("When: " .. def.timing)
    grp:Label(def.desc)
end

-- ─── State ──────────────────────────────────────────────────────────────────

local defense = {
    casting   = false,
    cast_t0   = 0,
    cast_idx  = nil,
    cast_slot = nil,
    last_cast = 0,
    last_msg  = "",
    trigger   = "",
}

local defense_cache = { t = -1, lp = nil, by_id = {} }
local font_hud  = nil
local font_mono = nil

local HUD_LEFT     = 18
local HUD_WIDTH    = 280
local HUD_PAD_X    = 10
local HUD_PAD_Y    = 8
local HUD_OFFSET_Y = 180
local HUD_ROW_H    = 13
local HUD_LINE_H   = 15
local HUD_SECTION  = 8

-- ─── Helpers ────────────────────────────────────────────────────────────────

local function safe(fn)
    local ok, v = pcall(fn)
    return ok and v or nil
end

local function item_name_matches(name, patterns)
    if not name or not patterns then return false end
    local ln = string.lower(name)
    for i = 1, #patterns do
        if string.find(ln, string.lower(patterns[i]), 1, true) then
            return true
        end
    end
    return false
end

local function item_slot_ready(lp, slot)
    local ab = safe(function() return lp:get_ability_by_slot(slot) end)
    if not ab or not ab:valid() then return false end
    local st = safe(function() return ab:can_be_executed() end)
    if st == 0 or st == true or st == 23 then return true end
    local cd = safe(function() return ab:get_cooldown() end)
    return cd ~= nil and cd <= 0.05
end

local function item_status(lp, slot)
    local ab = safe(function() return lp:get_ability_by_slot(slot) end)
    if not ab or not ab:valid() then return "nil" end
    local st = safe(function() return ab:can_be_executed() end)
    if st == 0 then return "ready" end
    if st == 2 then return "cd" end
    if st == 10 then return "busy" end
    return "st=" .. tostring(st)
end

local function press_item_slot(cmd, item_idx, ability_slot)
    local mask = ITEM_INPUT_BY_IDX[item_idx]
    if mask then
        cmd:add_buttonstate1(mask)
        if cmd.add_buttonstate2 then cmd:add_buttonstate2(mask) end
    end
    local cast_bit = ability_slot
    if cast_bit == nil and item_idx then
        cast_bit = ITEM_SLOT_FIRST + (item_idx - 1)
    end
    if cast_bit ~= nil then
        cmd.execute_ability_indices = (cmd.execute_ability_indices or 0) | (1 << cast_bit)
    end
end

local function is_cast_locked(lp)
    for i = 0, 3 do
        local ab = safe(function() return lp:get_ability_by_slot(i) end)
        if ab and ab:valid() then
            if ab.m_bInCastDelay then return true end
            if ab.m_bChanneling then return true end
        end
    end
    return false
end

local function is_enemy(lp, ent)
    if not lp or not ent or not ent:valid() or not ent:is_alive() then return false end
    return lp.m_iTeamNum ~= ent.m_iTeamNum
end

local function defense_use_enabled(def)
    if not def or not ui.enable:Get() then return false end
    local w = ui_item[def.id]
    return w and w.use and w.use:Get() or false
end

local function scan_defense_slots(lp)
    local t = safe(function() return global_vars.framecount() end) or global_vars.curtime()
    if defense_cache.t == t and defense_cache.lp == lp then
        return defense_cache.by_id
    end

    local by_id = {}
    for i = 0, 3 do
        local slot = ITEM_SLOT_FIRST + i
        local ab = safe(function() return lp:get_ability_by_slot(slot) end)
        if ab and ab:valid() then
            local name = safe(function() return ab:get_name() end)
            if name then
                for j = 1, #DEFENSE_ITEMS do
                    local def = DEFENSE_ITEMS[j]
                    if item_name_matches(name, def.patterns) and not by_id[def.id] then
                        by_id[def.id] = {
                            def = def,
                            slot = slot,
                            idx = i + 1,
                            name = name,
                            ready = item_slot_ready(lp, slot),
                            status = item_status(lp, slot),
                        }
                    end
                end
            end
        end
    end

    defense_cache = { t = t, lp = lp, by_id = by_id }
    return by_id
end

local function get_lp_hp_pct(lp)
    local hp = lp.m_iHealth or 0
    local ok, max_hp = pcall(lp.get_max_health, lp)
    if not ok or not max_hp or max_hp <= 0 then return 1 end
    return hp / max_hp
end

local function count_nearby_enemies(lp, radius_units)
    local origin = safe(function() return lp:get_origin() end)
    if not origin then return 0 end
    local count = 0
    for _, pawn in ipairs(entity_list.by_class_name("C_CitadelPlayerPawn")) do
        if is_enemy(lp, pawn) then
            local pos = safe(function() return pawn:get_origin() end)
            if pos then
                local dx = pos.x - origin.x
                local dy = pos.y - origin.y
                local dz = pos.z - origin.z
                if math.sqrt(dx * dx + dy * dy + dz * dz) <= radius_units then
                    count = count + 1
                end
            end
        end
    end
    return count
end

local function lp_has_debuff(lp)
    local ok, mods = pcall(lp.get_modifiers, lp)
    if not ok or not mods then return false end
    for _, mod in ipairs(mods) do
        local name = safe(function() return mod:get_name() end) or ""
        local ln = string.lower(name)
        for i = 1, #DEBUFF_PATTERNS do
            if string.find(ln, DEBUFF_PATTERNS[i], 1, true) then
                return true
            end
        end
    end
    return false
end

local function defense_order_kinds()
    local idx = (ui.queue_order:Get() or 0) + 1
    return DEFENSE_ORDERS[idx] or DEFENSE_ORDERS[1]
end

local function build_defense_queue(lp, mode)
    local queue = {}
    local by_id = scan_defense_slots(lp)
    local order = defense_order_kinds()

    local kinds_to_use = {}
    if mode == "debuff" then
        kinds_to_use[DEFENSE_KIND.CLEANSE] = true
    elseif mode == "panic" then
        for k = 1, 4 do kinds_to_use[k] = true end
    else
        for i = 1, #order do
            kinds_to_use[order[i]] = true
        end
        if ui.use_on_debuff:Get() and lp_has_debuff(lp) then
            kinds_to_use[DEFENSE_KIND.CLEANSE] = true
        end
    end

    for i = 1, #DEFENSE_ITEMS do
        local def = DEFENSE_ITEMS[i]
        if kinds_to_use[def.kind] and defense_use_enabled(def) then
            local owned = by_id[def.id]
            if owned and owned.ready then
                queue[#queue + 1] = owned
            end
        end
    end

    table.sort(queue, function(a, b)
        if a.def.kind ~= b.def.kind then return a.def.kind < b.def.kind end
        return a.def.order < b.def.order
    end)

    if mode == "hp" or mode == "panic" then
        local kind_seq = defense_order_kinds()
        table.sort(queue, function(a, b)
            local ai, bi = 99, 99
            for i = 1, #kind_seq do
                if kind_seq[i] == a.def.kind then ai = i end
                if kind_seq[i] == b.def.kind then bi = i end
            end
            if ai ~= bi then return ai < bi end
            return a.def.order < b.def.order
        end)
    end

    return queue
end

local function get_defense_trigger(lp, panic)
    if panic then return "panic" end
    local hp_pct = get_lp_hp_pct(lp)

    if ui.use_on_debuff:Get() and lp_has_debuff(lp) and hp_pct <= ui.debuff_hp_max:Get() / 100.0 then
        return "debuff"
    end

    if hp_pct > ui.hp_threshold:Get() / 100.0 then
        return nil
    end

    if ui.require_threat:Get() then
        local radius = ui.threat_radius_m:Get() * UNIT_METER
        local n = count_nearby_enemies(lp, radius)
        if n < ui.min_enemies:Get() then return nil end
    end

    return "hp"
end

local function external_combo_blocks()
    if ui.allow_during_combo:Get() then return false end
    if ParadoxCombo and ParadoxCombo.is_combo_active then
        return ParadoxCombo.is_combo_active()
    end
    return false
end

local function defense_can_run(lp)
    if not ui.enable:Get() then return false end
    if external_combo_blocks() then return false end
    if is_cast_locked(lp) then return false end
    return true
end

local function run_auto_defense(cmd, lp)
    if not defense_can_run(lp) then
        if defense.casting then
            defense.casting = false
            defense.cast_idx = nil
            defense.cast_slot = nil
        end
        return false
    end

    local now = global_vars.curtime()

    if defense.casting then
        if defense.cast_idx and defense.cast_slot then
            press_item_slot(cmd, defense.cast_idx, defense.cast_slot)
        end
        local hold = ui.item_hold_ms:Get() / 1000.0
        if (now - defense.cast_t0) >= hold then
            defense.casting = false
            defense.cast_idx = nil
            defense.cast_slot = nil
        end
        return true
    end

    if (now - defense.last_cast) < ui.cooldown_ms:Get() / 1000.0 then
        return false
    end

    local panic = ui.panic_key:IsPressed()
    local trigger = get_defense_trigger(lp, panic)
    if not trigger then return false end

    local queue = build_defense_queue(lp, trigger)
    if #queue == 0 then
        defense.last_msg = "no item ready"
        return false
    end

    local entry = queue[1]
    press_item_slot(cmd, entry.idx, entry.slot)
    defense.casting = true
    defense.cast_t0 = now
    defense.cast_idx = entry.idx
    defense.cast_slot = entry.slot
    defense.last_cast = now
    defense.trigger = trigger
    defense.last_msg = string.format("%s (%s)", entry.def.name, trigger)
    return true
end

-- ─── HUD ──────────────────────────────────────────────────────────────────────

local function ensure_fonts()
    if not font_hud then
        font_hud = Render.LoadFont("Tahoma", Enum.FontCreate.FONTFLAG_ANTIALIAS)
    end
    if not font_mono then
        font_mono = Render.LoadFont("Consolas", Enum.FontCreate.FONTFLAG_ANTIALIAS)
    end
end

local function hud_text_size(font, size, text)
    if not text or text == "" then return 0 end
    local ts = safe(function() return Render.TextSize(font, size, text) end)
    return ts and ts.x or (#text * size * 0.55)
end

local function truncate_to_width(font, size, text, max_w)
    if not text then return "" end
    if max_w <= 8 then return "…" end
    if hud_text_size(font, size, text) <= max_w then return text end
    local s = text
    while #s > 1 do
        s = string.sub(s, 1, #s - 1)
        local candidate = s .. "…"
        if hud_text_size(font, size, candidate) <= max_w then
            return candidate
        end
    end
    return "…"
end

local function draw_hud_panel_bg(px, py, w, h)
    if Render.FilledRect then
        Render.FilledRect(Vec2(px, py), Vec2(px + w, py + h), Color(6, 8, 14, 165), 6)
    end
    if Render.Rect then
        Render.Rect(Vec2(px, py), Vec2(px + w, py + h), Color(0, 150, 190, 40), 6, nil, 1)
    end
end

local function draw_hud_separator(x, y, w)
    Render.Line(Vec2(x, y), Vec2(x + w, y), Color(55, 75, 95, 90), 1)
end

local function draw_status_dot(px, py, col)
    if Render.FilledCircle then
        Render.FilledCircle(Vec2(px, py), 3.5, col)
    else
        Render.FilledRect(Vec2(px - 3, py - 3), Vec2(px + 3, py + 3), col, 2)
    end
end

local function draw_hud_text_right(font, size, text, right_x, y, col)
    if not text or text == "" then return end
    local w = hud_text_size(font, size, text)
    Render.Text(font, size, text, Vec2(right_x - w, y), col)
end

local function draw_hud_item_row(x, cy, inner_w, name, status_text, tag, dot_col, text_col, tag_col)
    draw_status_dot(x + 4, cy + 6, dot_col)

    local tag_w = 0
    if tag and tag ~= "" then
        tag_w = hud_text_size(font_mono, 9, tag) + 6
        draw_hud_text_right(font_mono, 9, tag, x + inner_w, cy + 1, tag_col)
    end

    local status_w = hud_text_size(font_mono, 10, status_text) + 6
    draw_hud_text_right(font_mono, 10, status_text, x + inner_w - tag_w, cy, text_col)

    local name_max_w = inner_w - tag_w - status_w - 18
    local name_text = truncate_to_width(font_mono, 10, name, name_max_w)
    Render.Text(font_mono, 10, name_text, Vec2(x + 12, cy), text_col)
end

local function draw_defense_hud(lp)
    if not ui.show_hud:Get() or not ui.enable:Get() then return end

    local content_h = 18 + HUD_SECTION + HUD_LINE_H + 13 + (#DEFENSE_ITEMS * HUD_ROW_H) + 4
    local panel_h = content_h + HUD_PAD_Y * 2
    local panel_w = HUD_WIDTH + HUD_PAD_X * 2

    local scr = Render.ScreenSize()
    local default_px = HUD_LEFT
    local default_py = math.floor((scr.y - panel_h) * 0.5 + HUD_OFFSET_Y)
    local px, py = default_px, default_py
    if HudDrag and HudDrag.apply then
        px, py = HudDrag.apply("defense", default_px, default_py, panel_w, panel_h)
    end
    local x = px + HUD_PAD_X
    local inner_w = HUD_WIDTH

    draw_hud_panel_bg(px, py, panel_w, panel_h)
    if HudDrag and HudDrag.draw_header_hint then
        HudDrag.draw_header_hint(px, py, panel_w)
    end

    local cy = py + HUD_PAD_Y
    Render.Text(font_hud, 13, "AUTO DEFENSE", Vec2(x, cy), Color(255, 140, 100, 255))
    cy = cy + 18

    cy = cy + 4
    draw_hud_separator(x, cy, inner_w)
    cy = cy + HUD_SECTION

    local by_id = scan_defense_slots(lp)
    local hp_pct = get_lp_hp_pct(lp) * 100
    local threat_n = count_nearby_enemies(lp, ui.threat_radius_m:Get() * UNIT_METER)
    local hp_col = Color(80, 255, 120, 230)
    if hp_pct <= ui.hp_threshold:Get() then hp_col = Color(255, 180, 80, 230) end
    if hp_pct <= ui.hp_threshold:Get() * 0.5 then hp_col = Color(255, 90, 90, 240) end

    Render.Text(font_hud, 12, "Defense", Vec2(x, cy), Color(180, 200, 220, 230))
    draw_hud_text_right(font_mono, 10, string.format("%.0f%% HP", hp_pct),
        x + inner_w, cy + 1, hp_col)
    cy = cy + HUD_LINE_H

    local threat_msg = string.format("threat: %d  |  %s",
        threat_n, defense.last_msg ~= "" and defense.last_msg or "ok")
    Render.Text(font_mono, 10,
        truncate_to_width(font_mono, 10, threat_msg, inner_w),
        Vec2(x, cy), Color(150, 165, 180, 215))
    cy = cy + 13

    for i = 1, #DEFENSE_ITEMS do
        local def = DEFENSE_ITEMS[i]
        local owned = by_id[def.id]
        local dot_col, status_text, text_col

        if not owned then
            dot_col = Color(70, 75, 85, 180)
            status_text = "—"
            text_col = Color(95, 100, 110, 175)
        elseif owned.ready then
            dot_col = Color(70, 230, 110, 240)
            status_text = string.format("S%d", owned.idx)
            text_col = Color(195, 205, 215, 235)
        elseif owned.status == "cd" then
            dot_col = Color(255, 170, 70, 240)
            status_text = string.format("S%d", owned.idx)
            text_col = Color(220, 175, 120, 230)
        else
            dot_col = Color(160, 165, 175, 210)
            status_text = string.format("S%d", owned.idx)
            text_col = Color(175, 180, 190, 220)
        end

        if defense_use_enabled(def) then
            text_col = Color(
                math.min(255, (text_col.r or 195) + 15),
                math.min(255, (text_col.g or 205) + 15),
                math.min(255, (text_col.b or 215) + 15),
                text_col.a or 235)
        end

        local tag = defense_use_enabled(def) and "auto" or ""
        draw_hud_item_row(x, cy, inner_w, def.name, status_text, tag, dot_col, text_col,
            Color(255, 140, 100, 170))
        cy = cy + HUD_ROW_H
    end
end

-- ─── Callbacks ──────────────────────────────────────────────────────────────

callback.on_createmove:set(function(cmd)
    local lp = entity_list.local_pawn()
    if not lp or not lp:valid() or not lp:is_alive() then
        if defense.casting then
            defense.casting = false
            defense.cast_idx = nil
            defense.cast_slot = nil
        end
        return
    end
    run_auto_defense(cmd, lp)
end)

callback.on_draw:set(function()
    if not ui.show_hud:Get() or not ui.enable:Get() then return end
    ensure_fonts()

    local lp = entity_list.local_pawn()
    if not lp or not lp:valid() or not lp:is_alive() then return end

    draw_defense_hud(lp)
end)

print("[Auto Defense] Carregado — Miscellaneous → Utility → Auto Defense")
print("[Auto Defense] 14 itens: cleanse, barreira, cura e survive")
