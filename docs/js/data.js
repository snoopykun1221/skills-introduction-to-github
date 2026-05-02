/**
 * Japan Travel Guide — Prefecture Master Data
 *
 * ▼▼▼ 収益化セットアップ ▼▼▼
 * 下の AFF_IDS に各 ASP のアフィリエイト ID を入れると、
 * 全アイテムのリンクが自動でアフィリエイト URL に置換されます。
 * 詳細は docs/MONETIZATION.md を参照。
 */
window.JAPAN_DATA = (() => {

  // ★公開前に必ず差し替えてください★
  const AFF_IDS = {
    // バリューコマース sid (例: "1234567")
    valuecommerce_sid:    "YOUR_VC_SID",
    // バリューコマース pid (案件ごとに異なる)
    vc_pid_jalan:         "YOUR_VC_PID_JALAN",       // じゃらんnet
    vc_pid_rakuten:       "YOUR_VC_PID_RAKUTEN",     // 楽天トラベル
    vc_pid_gnavi:         "YOUR_VC_PID_GNAVI",       // ぐるなび
    vc_pid_tabelog:       "YOUR_VC_PID_TABELOG",     // 食べログ
    vc_pid_ikyu:          "YOUR_VC_PID_IKYU",        // 一休
    // A8.net 案件ID
    a8_id_asoview:        "YOUR_A8_ASOVIEW",         // アソビュー！
    // もしも (msmstats) — 楽天市場の物販
    moshimo_id:           "YOUR_MOSHIMO_ID",
    // Amazon アソシエイト tag
    amazon_tag:           "nipponmapguid-22"
  };

  /* ---------- アフィリエイト URL 生成ヘルパー ---------- */
  // バリューコマース MyLink 形式 (実運用では発行済みリンクを直接埋める形でもOK)
  const vcLink = (pid, deepLink) =>
    `https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=${AFF_IDS.valuecommerce_sid}&pid=${pid}&vc_url=${encodeURIComponent(deepLink)}`;

  // A8.net 形式
  const a8Link = (a8Id, deepLink) =>
    `https://px.a8.net/svt/ejp?a8mat=${a8Id}&a8ejpredirect=${encodeURIComponent(deepLink)}`;

  // 各サービスへのリンク生成
  const link = {
    jalan:      (path)   => vcLink(AFF_IDS.vc_pid_jalan,   `https://www.jalan.net/${path}`),
    rakuten:    (path)   => vcLink(AFF_IDS.vc_pid_rakuten, `https://travel.rakuten.co.jp/${path}`),
    gnavi:      (path)   => vcLink(AFF_IDS.vc_pid_gnavi,   `https://r.gnavi.co.jp/${path}`),
    tabelog:    (path)   => vcLink(AFF_IDS.vc_pid_tabelog, `https://tabelog.com/${path}`),
    ikyu:       (path)   => vcLink(AFF_IDS.vc_pid_ikyu,    `https://restaurant.ikyu.com/${path}`),
    asoview:    (path)   => a8Link(AFF_IDS.a8_id_asoview,  `https://www.asoview.com/${path}`),
    amazon:     (kw)     => `https://www.amazon.co.jp/s?k=${encodeURIComponent(kw)}&tag=${AFF_IDS.amazon_tag}`
  };

  const REGION_LABEL = {
    hokkaido: "北海道", tohoku: "東北", kanto: "関東", chubu: "中部",
    kansai: "近畿", chugoku: "中国", shikoku: "四国", kyushu: "九州・沖縄"
  };

  // 各都道府県のサンプル4カテゴリ
  // 実運用ではここを CMS / JSON から読み込む形に拡張
  const sample = (prefId, prefName, prefSlug) => ({
    food: [
      { id: "f1", name: `${prefName}名物 朝獲れ海鮮丼の店`, tag: "TikTok 320万再生", emoji: "🍣",
        desc: `${prefName}の海の幸を贅沢にのせた一杯。地元民が並ぶ朝の名店。`,
        source: "じゃらんnet", url: link.jalan(`kankou/${prefSlug}/`) },
      { id: "f2", name: `${prefName}ラーメン 行列の老舗`, tag: "Instagram保存数1.2万", emoji: "🍜",
        desc: "深夜まで行列が絶えない、地元で40年愛される一杯。",
        source: "ぐるなび", url: link.gnavi(`area/${prefSlug}/rs/`) },
      { id: "f3", name: `${prefName} 隠れ家 焼鳥`, tag: "予約困難", emoji: "🍢",
        desc: "カウンター8席のみ。3ヶ月先まで予約満席の名店。",
        source: "一休.comレストラン", url: link.ikyu(`japanese/${prefSlug}/`) }
    ],
    spot: [
      { id: "s1", name: `${prefName} 絶景展望台`, tag: "夕日スポット", emoji: "🌅",
        desc: "SNSで話題の絶景。日没30分前到着がおすすめ。",
        source: "じゃらん観光", url: link.jalan(`kankou/${prefSlug}/spt/`) },
      { id: "s2", name: `${prefName}城・歴史散策`, tag: "ライトアップ夜景", emoji: "🏯",
        desc: "夜のライトアップは必見。御朱印も人気。",
        source: "楽天トラベル観光", url: link.rakuten(`movement/${prefSlug}/`) }
    ],
    shrine: [
      { id: "sh1", name: `${prefName} 縁結び神社`, tag: "御朱印映え", emoji: "⛩",
        desc: "縁結び・恋愛成就で有名。早朝参拝が清々しい。",
        source: "じゃらん観光", url: link.jalan(`kankou/${prefSlug}/g2_22/`) }
    ],
    experience: [
      { id: "e1", name: `${prefName} 伝統工芸 体験工房`, tag: "1時間〜", emoji: "🎎",
        desc: "地元職人と作る、世界に一つの旅の思い出。",
        source: "アソビュー！", url: link.asoview(`channel/${prefSlug}/`) },
      { id: "e2", name: `${prefName}のお土産 まとめ`, tag: "Amazon即配", emoji: "🎁",
        desc: "現地で買い忘れても大丈夫。家から注文できる名産品。",
        source: "Amazon", url: link.amazon(`${prefName} お土産`) }
    ]
  });

  // 47都道府県マスター (gridPos = CSSグリッド上の位置)
  const prefectures = [
    { id: "hokkaido", slug: "010000", name: "北海道", kanji: "北海道", region: "hokkaido", capital: "札幌市", tags: "#北海道グルメ #小樽", gridPos: { col: 9, row: 1, span: 2 }, large: true },

    { id: "aomori",    slug: "020000", name: "青森",   kanji: "青森",  region: "tohoku", capital: "青森市",     tags: "#ねぶた #りんご",     gridPos: { col: 9,  row: 3 } },
    { id: "akita",     slug: "050000", name: "秋田",   kanji: "秋田",  region: "tohoku", capital: "秋田市",     tags: "#きりたんぽ",         gridPos: { col: 8,  row: 3 } },
    { id: "iwate",     slug: "030000", name: "岩手",   kanji: "岩手",  region: "tohoku", capital: "盛岡市",     tags: "#わんこそば",         gridPos: { col: 10, row: 3 } },
    { id: "yamagata",  slug: "060000", name: "山形",   kanji: "山形",  region: "tohoku", capital: "山形市",     tags: "#さくらんぼ #銀山温泉", gridPos: { col: 8,  row: 4 } },
    { id: "miyagi",    slug: "040000", name: "宮城",   kanji: "宮城",  region: "tohoku", capital: "仙台市",     tags: "#牛タン #松島",       gridPos: { col: 10, row: 4 } },
    { id: "fukushima", slug: "070000", name: "福島",   kanji: "福島",  region: "tohoku", capital: "福島市",     tags: "#会津若松 #磐梯山",   gridPos: { col: 9,  row: 5 } },

    { id: "ibaraki",   slug: "080000", name: "茨城",   kanji: "茨城",  region: "kanto",  capital: "水戸市",     tags: "#納豆 #ひたち海浜",   gridPos: { col: 10, row: 5 } },
    { id: "tochigi",   slug: "090000", name: "栃木",   kanji: "栃木",  region: "kanto",  capital: "宇都宮市",   tags: "#日光 #餃子",         gridPos: { col: 9,  row: 6 } },
    { id: "gunma",     slug: "100000", name: "群馬",   kanji: "群馬",  region: "kanto",  capital: "前橋市",     tags: "#草津温泉",           gridPos: { col: 8,  row: 6 } },
    { id: "saitama",   slug: "110000", name: "埼玉",   kanji: "埼玉",  region: "kanto",  capital: "さいたま市", tags: "#川越 #秩父",         gridPos: { col: 9,  row: 7 } },
    { id: "tokyo",     slug: "130000", name: "東京",   kanji: "東京",  region: "kanto",  capital: "新宿区",     tags: "#東京グルメ #浅草",   gridPos: { col: 10, row: 7 } },
    { id: "chiba",     slug: "120000", name: "千葉",   kanji: "千葉",  region: "kanto",  capital: "千葉市",     tags: "#房総 #成田",         gridPos: { col: 11, row: 6 } },
    { id: "kanagawa",  slug: "140000", name: "神奈川", kanji: "神奈川",region: "kanto",  capital: "横浜市",     tags: "#横浜 #鎌倉 #箱根",   gridPos: { col: 10, row: 8 } },

    { id: "niigata",   slug: "150000", name: "新潟",   kanji: "新潟",  region: "chubu",  capital: "新潟市",     tags: "#日本酒 #米",         gridPos: { col: 8,  row: 5 } },
    { id: "toyama",    slug: "160000", name: "富山",   kanji: "富山",  region: "chubu",  capital: "富山市",     tags: "#立山黒部",           gridPos: { col: 7,  row: 6 } },
    { id: "ishikawa",  slug: "170000", name: "石川",   kanji: "石川",  region: "chubu",  capital: "金沢市",     tags: "#金沢 #兼六園",       gridPos: { col: 6,  row: 6 } },
    { id: "fukui",     slug: "180000", name: "福井",   kanji: "福井",  region: "chubu",  capital: "福井市",     tags: "#東尋坊 #永平寺",     gridPos: { col: 6,  row: 7 } },
    { id: "yamanashi", slug: "190000", name: "山梨",   kanji: "山梨",  region: "chubu",  capital: "甲府市",     tags: "#富士山 #ぶどう",     gridPos: { col: 9,  row: 8 } },
    { id: "nagano",    slug: "200000", name: "長野",   kanji: "長野",  region: "chubu",  capital: "長野市",     tags: "#軽井沢 #上高地",     gridPos: { col: 8,  row: 7 } },
    { id: "gifu",      slug: "210000", name: "岐阜",   kanji: "岐阜",  region: "chubu",  capital: "岐阜市",     tags: "#白川郷 #飛騨高山",   gridPos: { col: 7,  row: 7 } },
    { id: "shizuoka",  slug: "220000", name: "静岡",   kanji: "静岡",  region: "chubu",  capital: "静岡市",     tags: "#富士山 #茶 #伊豆",   gridPos: { col: 8,  row: 8 } },
    { id: "aichi",     slug: "230000", name: "愛知",   kanji: "愛知",  region: "chubu",  capital: "名古屋市",   tags: "#名古屋めし",         gridPos: { col: 7,  row: 8 } },

    { id: "mie",       slug: "240000", name: "三重",   kanji: "三重",  region: "kansai", capital: "津市",       tags: "#伊勢神宮 #松阪",     gridPos: { col: 6,  row: 8 } },
    { id: "shiga",     slug: "250000", name: "滋賀",   kanji: "滋賀",  region: "kansai", capital: "大津市",     tags: "#琵琶湖",             gridPos: { col: 5,  row: 7 } },
    { id: "kyoto",     slug: "260000", name: "京都",   kanji: "京都",  region: "kansai", capital: "京都市",     tags: "#京都グルメ #祇園",   gridPos: { col: 5,  row: 6 } },
    { id: "osaka",     slug: "270000", name: "大阪",   kanji: "大阪",  region: "kansai", capital: "大阪市",     tags: "#たこ焼き #道頓堀",   gridPos: { col: 4,  row: 7 } },
    { id: "hyogo",     slug: "280000", name: "兵庫",   kanji: "兵庫",  region: "kansai", capital: "神戸市",     tags: "#神戸 #姫路城",       gridPos: { col: 4,  row: 6 } },
    { id: "nara",      slug: "290000", name: "奈良",   kanji: "奈良",  region: "kansai", capital: "奈良市",     tags: "#奈良公園 #大仏",     gridPos: { col: 5,  row: 8 } },
    { id: "wakayama",  slug: "300000", name: "和歌山", kanji: "和歌山",region: "kansai", capital: "和歌山市",   tags: "#熊野古道",           gridPos: { col: 4,  row: 8 } },

    { id: "tottori",   slug: "310000", name: "鳥取",   kanji: "鳥取",  region: "chugoku", capital: "鳥取市",    tags: "#鳥取砂丘",           gridPos: { col: 3,  row: 6 } },
    { id: "shimane",   slug: "320000", name: "島根",   kanji: "島根",  region: "chugoku", capital: "松江市",    tags: "#出雲大社",           gridPos: { col: 2,  row: 6 } },
    { id: "okayama",   slug: "330000", name: "岡山",   kanji: "岡山",  region: "chugoku", capital: "岡山市",    tags: "#倉敷 #桃太郎",       gridPos: { col: 3,  row: 7 } },
    { id: "hiroshima", slug: "340000", name: "広島",   kanji: "広島",  region: "chugoku", capital: "広島市",    tags: "#宮島 #お好み焼き",   gridPos: { col: 2,  row: 7 } },
    { id: "yamaguchi", slug: "350000", name: "山口",   kanji: "山口",  region: "chugoku", capital: "山口市",    tags: "#角島大橋 #ふぐ",     gridPos: { col: 1,  row: 7 } },

    { id: "kagawa",    slug: "370000", name: "香川",   kanji: "香川",  region: "shikoku", capital: "高松市",    tags: "#うどん",             gridPos: { col: 3,  row: 8 } },
    { id: "tokushima", slug: "360000", name: "徳島",   kanji: "徳島",  region: "shikoku", capital: "徳島市",    tags: "#阿波踊り #鳴門",     gridPos: { col: 4,  row: 9 } },
    { id: "ehime",     slug: "380000", name: "愛媛",   kanji: "愛媛",  region: "shikoku", capital: "松山市",    tags: "#道後温泉 #みかん",   gridPos: { col: 2,  row: 8 } },
    { id: "kochi",     slug: "390000", name: "高知",   kanji: "高知",  region: "shikoku", capital: "高知市",    tags: "#カツオ #四万十川",   gridPos: { col: 3,  row: 9 } },

    { id: "fukuoka",   slug: "400000", name: "福岡",   kanji: "福岡",  region: "kyushu", capital: "福岡市",    tags: "#博多 #もつ鍋",       gridPos: { col: 1,  row: 8 } },
    { id: "saga",      slug: "410000", name: "佐賀",   kanji: "佐賀",  region: "kyushu", capital: "佐賀市",    tags: "#呼子イカ #有田焼",   gridPos: { col: 1,  row: 9 } },
    { id: "nagasaki",  slug: "420000", name: "長崎",   kanji: "長崎",  region: "kyushu", capital: "長崎市",    tags: "#ハウステンボス #ちゃんぽん", gridPos: { col: 1,  row: 10 } },
    { id: "kumamoto",  slug: "430000", name: "熊本",   kanji: "熊本",  region: "kyushu", capital: "熊本市",    tags: "#阿蘇 #熊本城",       gridPos: { col: 2,  row: 9 } },
    { id: "oita",      slug: "440000", name: "大分",   kanji: "大分",  region: "kyushu", capital: "大分市",    tags: "#別府温泉 #由布院",   gridPos: { col: 2,  row: 10 } },
    { id: "miyazaki",  slug: "450000", name: "宮崎",   kanji: "宮崎",  region: "kyushu", capital: "宮崎市",    tags: "#高千穂峡",           gridPos: { col: 3,  row: 10 } },
    { id: "kagoshima", slug: "460000", name: "鹿児島", kanji: "鹿児島",region: "kyushu", capital: "鹿児島市",  tags: "#屋久島 #黒豚",       gridPos: { col: 3,  row: 11 } },
    { id: "okinawa",   slug: "470000", name: "沖縄",   kanji: "沖縄",  region: "kyushu", capital: "那覇市",    tags: "#美ら海 #石垣島",     gridPos: { col: 1,  row: 11 } }
  ];

  prefectures.forEach(p => {
    p.items = sample(p.id, p.name, p.slug);
    p.regionLabel = REGION_LABEL[p.region];
  });

  return { prefectures, REGION_LABEL, AFF_IDS };
})();
