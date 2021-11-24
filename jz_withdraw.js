/*
作者：坤坤

appstore 搜索九章头条   
1W金币=1元
点提现没反应的：退出登录，使用微信登录，绑定原账号的手机号即可
自动提现：自动提0.3元
cron 每天上线50篇文章，超过就是1金币

圈x  其他自己编写
[rewrite_local]
https://api.st615.com/v1/user/info? url script-request-header https://raw.githubusercontent.com/xl2101200/-/main/jztt.js

[mitm]
api.st615.com

自动提现，从30-5-2-0.3,不需要设置，把token填入tokenArr里面
*/

const jobname = '九章头条'
const $ = Env(jobname)
const notify = $.isNode() ? require('./sendNotify') : '';

let taskmap = new Map();
let articleidarr = [];
let username="";
let tsxx="";	//推送信息
let ts=true;	//推送开关
let money=0;
let trytx=3;	//尝试提现次数

//ck顺序：...
let TokenArr = [
    process.env.jzttur131,
    process.env.jzttur132,
    process.env.jzttur191,
    process.env.jztturpg,
    process.env.jztturl1,
    process.env.jztturl1'
];
var hours = new Date().getHours();
!(async () => {
    await all();
})()
    .catch((e) => {
        $.log('', `❌ ${$.name}, 失败! 原因: ${e}!`, '')
    })
    .finally(() => {
        $.done();
    })

async function all() {
    //nodejs运行
	$.log(`总共${TokenArr.length}个账号`);
    for (let i = 0; i < TokenArr.length; i++) {
		trytx=3
        $.log(`\n开始执行第${i+1}个账号\n`);
		var time = new Date().getTime();
		var txtime=formatDateTime(time);
        Token=TokenArr[i];
		
		await userinfo();
		
		$.log(`${username} 脚本开始时间:${txtime}`);		
		tsxx += `\n${username} 脚本开始时间:${txtime}\n`;
		//提现
		//$.log("【九章头条提现】");
        if (hours < 1) {
		for (let i = 0; i < 3; i++) {
            await ArticleShare();
            await $.wait(randomNum(0, 5000));
        }
        }
		await $.wait(randomNum(5000, 8000));
		await CashAD();
		await $.wait(3000);
		await NineWithDraw(money);
		await $.wait(1000);		
    }
	//推送信息
	if (ts){
		if ($.isNode()){await notify.sendNotify($.name, tsxx );}
	}
}

//账号信息
function userinfo() {
    return new Promise((resolve, reject) => {
        const url = "https://api.st615.com/v1/user/info?token="+Token;
        const headers = {};
        const request = {
            url: url,
            headers: headers,
        };

        $.get(request, async (error, response, data) => {
            try {
                //$.log(data);
                let result = JSON.parse(data);
				if (result.code == 0){
					username=result.data.name;
					money=result.data.money
					$.log(`【用户】${username}`);
					$.log(`【余额】${money}`);
					$.log(`---------------------------`);
				}
            } catch (e) {
                $.log(e)
            }
            resolve();
        })
    })
}
async function NineWithDraw(money) {
  return new Promise((resolve, reject) => {
    const url = "https://api.st615.com/v1/cash/withdraw-new";
    const headers = {};
	let cash=0
	if (money>=30)cash=30;
	else if (money>=5)cash=5;
	else if (money>=2)cash=2;
	else if (money>=0.3)cash=0.3;
	
	if (cash==0){
		console.log('余额不足，跳过提现')
		return
	}
	const body = `token=${Token}&type=1&money=${cash}`;
	var time = new Date().getTime();
	var txtime=formatDateTime(time);
	$.log(`${username} 提现时间:${txtime}，尝试提现${cash}`);
	tsxx += `提现时间:${txtime},余额${money},尝试提现${cash}\n`;

    const request = {
      url: url,
      headers: headers,
      body: body
    };

    $.post(request, async (error, response, data) => {
      try {
        let result = JSON.parse(data);
        $.log(`【提现结果】${result.msg}`);
		tsxx += `提现结果:${result.msg}\n`;
		if (result.msg=='每天仅限提现一次!' || result.msg=='操作过于频繁!' ) trytx=0;
		if (result.msg!='提交成功，请耐心等待审核!' && trytx>0){
			let newmoney=parseInt(cash)-0.1
			if (newmoney>=0.3){
			tsxx += `提现:${cash}失败,设置提现金额为${newmoney}\n`;
			await $.wait(3000);
			trytx =trytx-1
			await NineWithDraw(newmoney);
			}
		}
      } catch (e) {
        $.log(e)
      }
      resolve();
    })
  })
}

function ArticleShare() {
    return new Promise((resolve, reject) => {
        const url = "https://api.st615.com/v1/article/share";
        const headers = {};
        const body = `token=${Token}`;
        const request = {
            url: url,
            headers: headers,
            body: body
        };

        $.post(request, async (error, response, data) => {
            try {
                let result = JSON.parse(data);
                if (result.code == 0) {
                    $.log(`【分享】${result.msg}`)
                }
            } catch (e) {
                $.log(e)
            }
            resolve();
        })
    })
}

function CashAD() {
  return new Promise((resolve, reject) => {
    const url = `https://api.st615.com/v1/cash/ads?token=${Token}&source=cash`;
    const headers = {};
    const request = {
      url: url,
      headers: headers
    };

    $.get(request, async (error, response, data) => {
      try {
        //$.log(data);
        let result = JSON.parse(data);
        $.log(`【提现视频】${result.msg}`)
      } catch (e) {
        $.log(e)
      }
      resolve();
    })
  })
}


function formatDateTime(inputTime) {
  var date = new Date(inputTime);
  var y = date.getFullYear();
  var m = date.getMonth() + 1;
  m = m < 10 ? ('0' + m) : m;
  var d = date.getDate();
  d = d < 10 ? ('0' + d) : d;
  var h = date.getHours();
  h = h < 10 ? ('0' + h) : h;
  var minute = date.getMinutes();
  var second = date.getSeconds();
  minute = minute < 10 ? ('0' + minute) : minute;
  second = second < 10 ? ('0' + second) : second;
   return y + '-' + m + '-' + d + '  '+h+':'+minute;
};

function randomNum(minNum, maxNum) {
    switch (arguments.length) {
        case 1:
            return parseInt(Math.random() * minNum + 1, 10);
            break;
        case 2:
            return parseInt(Math.random() * (maxNum - minNum + 1) + minNum, 10);
            break;
        default:
            return 0;
            break;
    }
}

function Env(t,e){"undefined"!=typeof process&&JSON.stringify(process.env).indexOf("GITHUB")>-1&&process.exit(0);class s{constructor(t){this.env=t}send(t,e="GET"){t="string"==typeof t?{url:t}:t;let s=this.get;return"POST"===e&&(s=this.post),new Promise((e,i)=>{s.call(this,t,(t,s,r)=>{t?i(t):e(s)})})}get(t){return this.send.call(this.env,t)}post(t){return this.send.call(this.env,t,"POST")}}return new class{constructor(t,e){this.name=t,this.http=new s(this),this.data=null,this.dataFile="box.dat",this.logs=[],this.isMute=!1,this.isNeedRewrite=!1,this.logSeparator="\n",this.startTime=(new Date).getTime(),Object.assign(this,e),this.log("",`🔔${this.name}, 开始!`)}isNode(){return"undefined"!=typeof module&&!!module.exports}isQuanX(){return"undefined"!=typeof $task}isSurge(){return"undefined"!=typeof $httpClient&&"undefined"==typeof $loon}isLoon(){return"undefined"!=typeof $loon}toObj(t,e=null){try{return JSON.parse(t)}catch{return e}}toStr(t,e=null){try{return JSON.stringify(t)}catch{return e}}getjson(t,e){let s=e;const i=this.getdata(t);if(i)try{s=JSON.parse(this.getdata(t))}catch{}return s}setjson(t,e){try{return this.setdata(JSON.stringify(t),e)}catch{return!1}}getScript(t){return new Promise(e=>{this.get({url:t},(t,s,i)=>e(i))})}runScript(t,e){return new Promise(s=>{let i=this.getdata("@chavy_boxjs_userCfgs.httpapi");i=i?i.replace(/\n/g,"").trim():i;let r=this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout");r=r?1*r:20,r=e&&e.timeout?e.timeout:r;const[o,h]=i.split("@"),n={url:`http://${h}/v1/scripting/evaluate`,body:{script_text:t,mock_type:"cron",timeout:r},headers:{"X-Key":o,Accept:"*/*"}};this.post(n,(t,e,i)=>s(i))}).catch(t=>this.logErr(t))}loaddata(){if(!this.isNode())return{};{this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e);if(!s&&!i)return{};{const i=s?t:e;try{return JSON.parse(this.fs.readFileSync(i))}catch(t){return{}}}}}writedata(){if(this.isNode()){this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e),r=JSON.stringify(this.data);s?this.fs.writeFileSync(t,r):i?this.fs.writeFileSync(e,r):this.fs.writeFileSync(t,r)}}lodash_get(t,e,s){const i=e.replace(/\[(\d+)\]/g,".$1").split(".");let r=t;for(const t of i)if(r=Object(r)[t],void 0===r)return s;return r}lodash_set(t,e,s){return Object(t)!==t?t:(Array.isArray(e)||(e=e.toString().match(/[^.[\]]+/g)||[]),e.slice(0,-1).reduce((t,s,i)=>Object(t[s])===t[s]?t[s]:t[s]=Math.abs(e[i+1])>>0==+e[i+1]?[]:{},t)[e[e.length-1]]=s,t)}getdata(t){let e=this.getval(t);if(/^@/.test(t)){const[,s,i]=/^@(.*?)\.(.*?)$/.exec(t),r=s?this.getval(s):"";if(r)try{const t=JSON.parse(r);e=t?this.lodash_get(t,i,""):e}catch(t){e=""}}return e}setdata(t,e){let s=!1;if(/^@/.test(e)){const[,i,r]=/^@(.*?)\.(.*?)$/.exec(e),o=this.getval(i),h=i?"null"===o?null:o||"{}":"{}";try{const e=JSON.parse(h);this.lodash_set(e,r,t),s=this.setval(JSON.stringify(e),i)}catch(e){const o={};this.lodash_set(o,r,t),s=this.setval(JSON.stringify(o),i)}}else s=this.setval(t,e);return s}getval(t){return this.isSurge()||this.isLoon()?$persistentStore.read(t):this.isQuanX()?$prefs.valueForKey(t):this.isNode()?(this.data=this.loaddata(),this.data[t]):this.data&&this.data[t]||null}setval(t,e){return this.isSurge()||this.isLoon()?$persistentStore.write(t,e):this.isQuanX()?$prefs.setValueForKey(t,e):this.isNode()?(this.data=this.loaddata(),this.data[e]=t,this.writedata(),!0):this.data&&this.data[e]||null}initGotEnv(t){this.got=this.got?this.got:require("got"),this.cktough=this.cktough?this.cktough:require("tough-cookie"),this.ckjar=this.ckjar?this.ckjar:new this.cktough.CookieJar,t&&(t.headers=t.headers?t.headers:{},void 0===t.headers.Cookie&&void 0===t.cookieJar&&(t.cookieJar=this.ckjar))}get(t,e=(()=>{})){t.headers&&(delete t.headers["Content-Type"],delete t.headers["Content-Length"]),this.isSurge()||this.isLoon()?(this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient.get(t,(t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status),e(t,s,i)})):this.isQuanX()?(this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>e(t))):this.isNode()&&(this.initGotEnv(t),this.got(t).on("redirect",(t,e)=>{try{if(t.headers["set-cookie"]){const s=t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString();s&&this.ckjar.setCookieSync(s,null),e.cookieJar=this.ckjar}}catch(t){this.logErr(t)}}).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>{const{message:s,response:i}=t;e(s,i,i&&i.body)}))}post(t,e=(()=>{})){if(t.body&&t.headers&&!t.headers["Content-Type"]&&(t.headers["Content-Type"]="application/x-www-form-urlencoded"),t.headers&&delete t.headers["Content-Length"],this.isSurge()||this.isLoon())this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient.post(t,(t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status),e(t,s,i)});else if(this.isQuanX())t.method="POST",this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>e(t));else if(this.isNode()){this.initGotEnv(t);const{url:s,...i}=t;this.got.post(s,i).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>{const{message:s,response:i}=t;e(s,i,i&&i.body)})}}time(t,e=null){const s=e?new Date(e):new Date;let i={"M+":s.getMonth()+1,"d+":s.getDate(),"H+":s.getHours(),"m+":s.getMinutes(),"s+":s.getSeconds(),"q+":Math.floor((s.getMonth()+3)/3),S:s.getMilliseconds()};/(y+)/.test(t)&&(t=t.replace(RegExp.$1,(s.getFullYear()+"").substr(4-RegExp.$1.length)));for(let e in i)new RegExp("("+e+")").test(t)&&(t=t.replace(RegExp.$1,1==RegExp.$1.length?i[e]:("00"+i[e]).substr((""+i[e]).length)));return t}msg(e=t,s="",i="",r){const o=t=>{if(!t)return t;if("string"==typeof t)return this.isLoon()?t:this.isQuanX()?{"open-url":t}:this.isSurge()?{url:t}:void 0;if("object"==typeof t){if(this.isLoon()){let e=t.openUrl||t.url||t["open-url"],s=t.mediaUrl||t["media-url"];return{openUrl:e,mediaUrl:s}}if(this.isQuanX()){let e=t["open-url"]||t.url||t.openUrl,s=t["media-url"]||t.mediaUrl;return{"open-url":e,"media-url":s}}if(this.isSurge()){let e=t.url||t.openUrl||t["open-url"];return{url:e}}}};if(this.isMute||(this.isSurge()||this.isLoon()?$notification.post(e,s,i,o(r)):this.isQuanX()&&$notify(e,s,i,o(r))),!this.isMuteLog){let t=["","==============📣系统通知📣=============="];t.push(e),s&&t.push(s),i&&t.push(i),console.log(t.join("\n")),this.logs=this.logs.concat(t)}}log(...t){t.length>0&&(this.logs=[...this.logs,...t]),console.log(t.join(this.logSeparator))}logErr(t,e){const s=!this.isSurge()&&!this.isQuanX()&&!this.isLoon();s?this.log("",`❗️${this.name}, 错误!`,t.stack):this.log("",`❗️${this.name}, 错误!`,t)}wait(t){return new Promise(e=>setTimeout(e,t))}done(t={}){const e=(new Date).getTime(),s=(e-this.startTime)/1e3;this.log("",`🔔${this.name}, 结束! 🕛 ${s} 秒`),this.log(),(this.isSurge()||this.isQuanX()||this.isLoon())&&$done(t)}}(t,e)}
