# 収益化セットアップガイド

このサイトは「アフィリエイト + ディスプレイ広告」のハイブリッドで収益化する設計です。
公開前に下記の手順で各種 ID を差し替えてください。

---

## 1. 推奨アフィリエイト・プログラム

### 旅行系(主軸 — KPI: 予約成立)
| サービス | ASP | 報酬目安 | 強み |
|---|---|---|---|
| 楽天トラベル | バリューコマース or もしも | 宿泊金額の 1% | 国内最大手・知名度 |
| じゃらんnet | バリューコマース | 宿泊1% / 体験 2-3% | 観光・体験予約も同居 |
| 一休.com (高級宿/レストラン) | バリューコマース | 1-2% | 客単価が高い |
| アソビュー！ | A8.net | 3-5% | 体験/アクティビティ最大手 |
| Booking.com / agoda | アクセストレード | 4% | インバウンド向け |
| エアトリ | A8.net | 2-3% | 航空券パック |

### 飲食店予約(KPI: 予約成立)
| サービス | ASP | 報酬目安 |
|---|---|---|
| ぐるなび | バリューコマース | 50-100円/件 |
| 食べログ | バリューコマース | 100円/件〜 |
| HOT PEPPER グルメ | A8.net | 100円/件 |

### 物販(お土産 / 旅行用品)
| サービス | ASP | 報酬目安 |
|---|---|---|
| 楽天市場 | もしもアフィリエイト | 0.5-2% |
| Amazon | Amazon アソシエイト | 0.5-8%(カテゴリ依存) |

### ディスプレイ広告
| サービス | 単価目安 | 条件 |
|---|---|---|
| **Google AdSense** | RPM 200-500円 | 王道。最初はこれ |
| Mediavine / Raptive | RPM 1,500-3,000円 | 月間 50,000PV〜 |

### 推奨 ASP 登録順
**A8.net → もしもアフィリエイト → バリューコマース → アクセストレード**
(A8 と もしも は審査ゆるめで初心者向け、バリュコマは案件単価が良い)

---

## 2. 各 ID の差し替え

### 2-1. アフィリエイト ID (`docs/js/data.js`)

ファイル冒頭の `AFF_IDS` を編集します。

```js
const AFF_IDS = {
  valuecommerce_sid:    "1234567",                  // バリューコマースの sid
  vc_pid_jalan:         "8810XXXXXX_8810XXXXXX",    // じゃらんnet の pid
  vc_pid_rakuten:       "8810XXXXXX_8810XXXXXX",    // 楽天トラベル の pid
  vc_pid_gnavi:         "8810XXXXXX_8810XXXXXX",    // ぐるなび の pid
  vc_pid_tabelog:       "8810XXXXXX_8810XXXXXX",    // 食べログ の pid
  vc_pid_ikyu:          "8810XXXXXX_8810XXXXXX",    // 一休 の pid
  a8_id_asoview:        "3HXXXXX+XXXXXX+XXXX+XXXXX",// A8.net マテリアル
  moshimo_id:           "あなたのもしもID",
  amazon_tag:           "yourtag-22"                // Amazon アソシエイト ID
};
```

各 pid / a8mat はバリューコマースや A8.net で「広告主と提携 → 広告原稿を見る」から取得できます。

### 2-2. Google Analytics 4 (`docs/index.html`)

`GA4_MEASUREMENT_ID` を `G-XXXXXXXXXX` に置換し、`<!-- -->` のコメントアウトを外します。

### 2-3. Google AdSense (`docs/index.html`)

1. AdSense に登録 → サイト承認を取得
2. `ADSENSE_CLIENT` を `ca-pub-XXXXXXXXXXXXXXXX` に置換
3. 広告ユニットを作成 → `data-ad-slot` の `YOUR_SLOT_ID_TOP` に slot ID を貼る
4. `<!-- -->` を外して有効化

---

## 3. KPI 計測

`docs/js/app.js` の `trackAffiliateClick()` で、アフィリエイトリンクのクリックを以下に送信します。

- `gtag('event', 'affiliate_click', {...})` — GA4 のカスタムイベント
- `dataLayer.push({...})` — Google Tag Manager 経由

GA4 側で「探索 → 自由形式 → イベント名 = `affiliate_click`」で
都道府県別 / カテゴリ別 / アイテム別のクリック数を可視化できます。

### 主要 KPI
| 指標 | 計測方法 |
|---|---|
| 都道府県別 PV | GA4 ページビュー + `prefecture_open` イベント |
| アフィリエイトCTR | `affiliate_click` ÷ ページビュー |
| アイテム別 CV | 各 ASP 管理画面の「サブID/参照元」 |
| EPC (1クリックあたり収益) | 報酬 ÷ クリック数 |

---

## 4. 公開前チェックリスト

- [ ] `AFF_IDS` をすべて本番 ID に差し替えた
- [ ] GA4 タグのコメントアウトを解除した
- [ ] AdSense サイト審査を通過し、コードを設置した
- [ ] `<meta property="og:image">` を追加した(OGP 画像 1200x630px)
- [ ] プライバシーポリシー・特定商取引表記を別ページで用意
- [ ] アフィリエイト表記(「当サイトは〜を利用しています」)が記載済み
- [ ] Google Search Console にサイト登録、サイトマップ送信
- [ ] 各都道府県の `items` を実データに置き換え(現状サンプル)

---

## 5. グロース戦略

1. **インバウンド SEO**: 「[県名] おすすめ 観光」「[県名] グルメ TikTok」狙い
2. **TikTok / Instagram 連携**: SNS 投稿の「プロフィールリンク」として活用
3. **Pinterest**: 旅行系は刺さる、画像と都道府県ページを紐づけ
4. **比較記事の追加**: 「[県名] ランチ おすすめ10選」など長文 SEO 記事を `posts/` に追加
5. **メールマガジン**: 都道府県登録機能を追加し、新着スポット通知 → リテンション
