/**
 * 47都道府県の基本情報 + おすすめスポットのサンプルデータ。
 * `gridPos` は map-grid 上の {col, row, span} を指定し、日本列島の形を再現する。
 * `items` は各カテゴリのサンプル（実運用時は CMS / DB から流し込み想定）。
 *
 * affiliateUrl は楽天トラベル / じゃらん / ぐるなび等のアフィリエイトリンクを想定。
 * 計測のため `?aff=<source>-<prefId>-<itemId>` を付与してクリック先で識別可能にする。
 */
window.JAPAN_DATA = (() => {
  const REGION_LABEL = {
    hokkaido: "北海道",
    tohoku: "東北",
    kanto: "関東",
    chubu: "中部",
    kansai: "近畿",
    chugoku: "中国",
    shikoku: "四国",
    kyushu: "九州・沖縄"
  };

  // ヘルパー: アフィリエイトURLを生成
  const aff = (base, source, prefId, itemId) =>
    `${base}?aff=${source}-${prefId}-${itemId}`;

  // サンプルアイテム生成 (デモ用 — 実運用ではCMS連携)
  const sample = (prefId, prefName) => ({
    food: [
      {
        id: "f1",
        name: `${prefName}名物 朝獲れ海鮮丼の店`,
        tag: "TikTok 320万再生",
        emoji: "🍣",
        desc: `${prefName}の海の幸を贅沢にのせた一杯。地元民が並ぶ朝の名店。`,
        source: "じゃらん遊び・体験予約",
        url: aff("https://www.jalan.net/kankou/", "jalan", prefId, "f1")
      },
      {
        id: "f2",
        name: `${prefName}ラーメン 行列の老舗`,
        tag: "Instagram保存数1.2万",
        emoji: "🍜",
        desc: "深夜まで行列が絶えない、地元で40年愛される一杯。",
        source: "ぐるなび",
        url: aff("https://r.gnavi.co.jp/area/", "gnavi", prefId, "f2")
      },
      {
        id: "f3",
        name: `${prefName} 隠れ家 焼鳥`,
        tag: "予約困難",
        emoji: "🍢",
        desc: "カウンター8席のみ。3ヶ月先まで予約満席の名店。",
        source: "一休.comレストラン",
        url: aff("https://restaurant.ikyu.com/", "ikyu", prefId, "f3")
      }
    ],
    spot: [
      {
        id: "s1",
        name: `${prefName} 絶景展望台`,
        tag: "夕日スポット",
        emoji: "🌅",
        desc: "SNSで話題の絶景。日没30分前到着がおすすめ。",
        source: "じゃらん",
        url: aff("https://www.jalan.net/kankou/", "jalan", prefId, "s1")
      },
      {
        id: "s2",
        name: `${prefName}城・歴史散策`,
        tag: "ライトアップ夜景",
        emoji: "🏯",
        desc: "夜のライトアップは必見。御朱印も人気。",
        source: "楽天トラベル観光",
        url: aff("https://travel.rakuten.co.jp/movement/", "rakuten", prefId, "s2")
      }
    ],
    shrine: [
      {
        id: "sh1",
        name: `${prefName} 縁結び神社`,
        tag: "御朱印映え",
        emoji: "⛩",
        desc: "縁結び・恋愛成就で有名。早朝参拝が清々しい。",
        source: "JTB体験",
        url: aff("https://www.jtb.co.jp/kaigai_opt/", "jtb", prefId, "sh1")
      }
    ],
    experience: [
      {
        id: "e1",
        name: `${prefName} 伝統工芸 体験工房`,
        tag: "1時間〜",
        emoji: "🎎",
        desc: "地元職人と作る、世界に一つの旅の思い出。",
        source: "アソビュー！",
        url: aff("https://www.asoview.com/", "asoview", prefId, "e1")
      }
    ]
  });

  // 47都道府県マスター
  // gridPos: 11列のグリッド上の {col, row} (1-indexed)
  // 日本列島の形を意識した配置
  const prefectures = [
    // 北海道
    { id: "hokkaido", name: "北海道", kanji: "北海道", region: "hokkaido", capital: "札幌市", tags: "#北海道グルメ #小樽", gridPos: { col: 9, row: 1, span: 2 }, large: true },

    // 東北 (青森〜福島) - 縦に積む
    { id: "aomori",   name: "青森",   kanji: "青森", region: "tohoku", capital: "青森市",     tags: "#ねぶた #りんご",     gridPos: { col: 9,  row: 3 } },
    { id: "akita",    name: "秋田",   kanji: "秋田", region: "tohoku", capital: "秋田市",     tags: "#きりたんぽ",         gridPos: { col: 8,  row: 3 } },
    { id: "iwate",    name: "岩手",   kanji: "岩手", region: "tohoku", capital: "盛岡市",     tags: "#わんこそば",         gridPos: { col: 10, row: 3 } },
    { id: "yamagata", name: "山形",   kanji: "山形", region: "tohoku", capital: "山形市",     tags: "#さくらんぼ #銀山温泉", gridPos: { col: 8,  row: 4 } },
    { id: "miyagi",   name: "宮城",   kanji: "宮城", region: "tohoku", capital: "仙台市",     tags: "#牛タン #松島",       gridPos: { col: 10, row: 4 } },
    { id: "fukushima",name: "福島",   kanji: "福島", region: "tohoku", capital: "福島市",     tags: "#会津若松 #磐梯山",    gridPos: { col: 9,  row: 5 } },

    // 関東
    { id: "ibaraki",  name: "茨城",   kanji: "茨城", region: "kanto",  capital: "水戸市",     tags: "#納豆 #ひたち海浜",   gridPos: { col: 10, row: 5 } },
    { id: "tochigi",  name: "栃木",   kanji: "栃木", region: "kanto",  capital: "宇都宮市",   tags: "#日光 #餃子",         gridPos: { col: 9,  row: 6 } },
    { id: "gunma",    name: "群馬",   kanji: "群馬", region: "kanto",  capital: "前橋市",     tags: "#草津温泉",           gridPos: { col: 8,  row: 6 } },
    { id: "saitama",  name: "埼玉",   kanji: "埼玉", region: "kanto",  capital: "さいたま市", tags: "#川越 #秩父",         gridPos: { col: 9,  row: 7 } },
    { id: "tokyo",    name: "東京",   kanji: "東京", region: "kanto",  capital: "新宿区",     tags: "#東京グルメ #浅草",   gridPos: { col: 10, row: 7 } },
    { id: "chiba",    name: "千葉",   kanji: "千葉", region: "kanto",  capital: "千葉市",     tags: "#房総 #成田",         gridPos: { col: 11, row: 6 } },
    { id: "kanagawa", name: "神奈川", kanji: "神奈川",region: "kanto",  capital: "横浜市",     tags: "#横浜 #鎌倉 #箱根",   gridPos: { col: 10, row: 8 } },

    // 中部
    { id: "niigata",  name: "新潟",   kanji: "新潟", region: "chubu",  capital: "新潟市",     tags: "#日本酒 #米",         gridPos: { col: 8,  row: 5 } },
    { id: "toyama",   name: "富山",   kanji: "富山", region: "chubu",  capital: "富山市",     tags: "#立山黒部",           gridPos: { col: 7,  row: 6 } },
    { id: "ishikawa", name: "石川",   kanji: "石川", region: "chubu",  capital: "金沢市",     tags: "#金沢 #兼六園",       gridPos: { col: 6,  row: 6 } },
    { id: "fukui",    name: "福井",   kanji: "福井", region: "chubu",  capital: "福井市",     tags: "#東尋坊 #永平寺",     gridPos: { col: 6,  row: 7 } },
    { id: "yamanashi",name: "山梨",   kanji: "山梨", region: "chubu",  capital: "甲府市",     tags: "#富士山 #ぶどう",     gridPos: { col: 9,  row: 8 } },
    { id: "nagano",   name: "長野",   kanji: "長野", region: "chubu",  capital: "長野市",     tags: "#軽井沢 #上高地",     gridPos: { col: 8,  row: 7 } },
    { id: "gifu",     name: "岐阜",   kanji: "岐阜", region: "chubu",  capital: "岐阜市",     tags: "#白川郷 #飛騨高山",   gridPos: { col: 7,  row: 7 } },
    { id: "shizuoka", name: "静岡",   kanji: "静岡", region: "chubu",  capital: "静岡市",     tags: "#富士山 #茶 #伊豆",   gridPos: { col: 8,  row: 8 } },
    { id: "aichi",    name: "愛知",   kanji: "愛知", region: "chubu",  capital: "名古屋市",   tags: "#名古屋めし",         gridPos: { col: 7,  row: 8 } },

    // 近畿
    { id: "mie",      name: "三重",   kanji: "三重", region: "kansai", capital: "津市",       tags: "#伊勢神宮 #松阪",     gridPos: { col: 6,  row: 8 } },
    { id: "shiga",    name: "滋賀",   kanji: "滋賀", region: "kansai", capital: "大津市",     tags: "#琵琶湖",             gridPos: { col: 5,  row: 7 } },
    { id: "kyoto",    name: "京都",   kanji: "京都", region: "kansai", capital: "京都市",     tags: "#京都グルメ #祇園",   gridPos: { col: 5,  row: 6 } },
    { id: "osaka",    name: "大阪",   kanji: "大阪", region: "kansai", capital: "大阪市",     tags: "#たこ焼き #道頓堀",   gridPos: { col: 4,  row: 7 } },
    { id: "hyogo",    name: "兵庫",   kanji: "兵庫", region: "kansai", capital: "神戸市",     tags: "#神戸 #姫路城",       gridPos: { col: 4,  row: 6 } },
    { id: "nara",     name: "奈良",   kanji: "奈良", region: "kansai", capital: "奈良市",     tags: "#奈良公園 #大仏",     gridPos: { col: 5,  row: 8 } },
    { id: "wakayama", name: "和歌山", kanji: "和歌山",region: "kansai", capital: "和歌山市",   tags: "#熊野古道",           gridPos: { col: 4,  row: 8 } },

    // 中国
    { id: "tottori",  name: "鳥取",   kanji: "鳥取", region: "chugoku", capital: "鳥取市",    tags: "#鳥取砂丘",           gridPos: { col: 3,  row: 6 } },
    { id: "shimane",  name: "島根",   kanji: "島根", region: "chugoku", capital: "松江市",    tags: "#出雲大社",           gridPos: { col: 2,  row: 6 } },
    { id: "okayama",  name: "岡山",   kanji: "岡山", region: "chugoku", capital: "岡山市",    tags: "#倉敷 #桃太郎",       gridPos: { col: 3,  row: 7 } },
    { id: "hiroshima",name: "広島",   kanji: "広島", region: "chugoku", capital: "広島市",    tags: "#宮島 #お好み焼き",   gridPos: { col: 2,  row: 7 } },
    { id: "yamaguchi",name: "山口",   kanji: "山口", region: "chugoku", capital: "山口市",    tags: "#角島大橋 #ふぐ",     gridPos: { col: 1,  row: 7 } },

    // 四国
    { id: "kagawa",   name: "香川",   kanji: "香川", region: "shikoku", capital: "高松市",    tags: "#うどん",             gridPos: { col: 3,  row: 8 } },
    { id: "tokushima",name: "徳島",   kanji: "徳島", region: "shikoku", capital: "徳島市",    tags: "#阿波踊り #鳴門",     gridPos: { col: 4,  row: 9 } },
    { id: "ehime",    name: "愛媛",   kanji: "愛媛", region: "shikoku", capital: "松山市",    tags: "#道後温泉 #みかん",   gridPos: { col: 2,  row: 8 } },
    { id: "kochi",    name: "高知",   kanji: "高知", region: "shikoku", capital: "高知市",    tags: "#カツオ #四万十川",   gridPos: { col: 3,  row: 9 } },

    // 九州・沖縄
    { id: "fukuoka",  name: "福岡",   kanji: "福岡", region: "kyushu", capital: "福岡市",    tags: "#博多 #もつ鍋",       gridPos: { col: 1,  row: 8 } },
    { id: "saga",     name: "佐賀",   kanji: "佐賀", region: "kyushu", capital: "佐賀市",    tags: "#呼子イカ #有田焼",   gridPos: { col: 1,  row: 9 } },
    { id: "nagasaki", name: "長崎",   kanji: "長崎", region: "kyushu", capital: "長崎市",    tags: "#ハウステンボス #ちゃんぽん", gridPos: { col: 1,  row: 10 } },
    { id: "kumamoto", name: "熊本",   kanji: "熊本", region: "kyushu", capital: "熊本市",    tags: "#阿蘇 #熊本城",       gridPos: { col: 2,  row: 9 } },
    { id: "oita",     name: "大分",   kanji: "大分", region: "kyushu", capital: "大分市",    tags: "#別府温泉 #由布院",   gridPos: { col: 2,  row: 10 } },
    { id: "miyazaki", name: "宮崎",   kanji: "宮崎", region: "kyushu", capital: "宮崎市",    tags: "#高千穂峡",           gridPos: { col: 3,  row: 10 } },
    { id: "kagoshima",name: "鹿児島", kanji: "鹿児島",region: "kyushu", capital: "鹿児島市",  tags: "#屋久島 #黒豚",       gridPos: { col: 3,  row: 11 } },
    { id: "okinawa",  name: "沖縄",   kanji: "沖縄", region: "kyushu", capital: "那覇市",    tags: "#美ら海 #石垣島",     gridPos: { col: 1,  row: 11 } }
  ];

  // 各都道府県にサンプルアイテムを付与
  prefectures.forEach(p => {
    p.items = sample(p.id, p.name);
    p.regionLabel = REGION_LABEL[p.region];
  });

  return { prefectures, REGION_LABEL };
})();
