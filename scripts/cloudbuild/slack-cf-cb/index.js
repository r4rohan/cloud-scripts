const { App, LogLevel } = require("@slack/bolt");
const { IncomingWebhook } = require('@slack/webhook');
const url = '[Slack-token]';

const webhook = new IncomingWebhook(url);

const app = new App({
  token: "xoxb-14351683122-4046474135153-9rvuBkm7McJCcl3JJoGTU9bZ", // from OAuth & Permissions tab of Slack APP.
  signingSecret: "04f50a5235ae53182141ba09d3efe7cb",
  // LogLevel can be imported and used to make debugging simpler
  logLevel: LogLevel.DEBUG
});

// subscribeSlack is the main function called by Cloud Functions.
module.exports.subscribeSlack = (pubSubEvent, context) => {
  const build = eventToBuild(pubSubEvent.data);
  const status = ['SUCCESS', 'FAILURE', 'INTERNAL_ERROR', 'TIMEOUT', 'CANCELLED'];
  if (status.indexOf(build.status) === -1) {
    return;
  }
  // Send message to Slack.
  const message = createSlackMessage(build);
  webhook.send(message);
};

// eventToBuild transforms pubsub event message to a build object.
const eventToBuild = (data) => {
  return JSON.parse(Buffer.from(data, 'base64').toString());
}

const DEFAULT_COLOR = '#4285F4'; // blue
const STATUS_COLOR = {
  SUCCESS: '#34A853', // green
  FAILURE: '#EA4335', // red
  TIMEOUT: '#FBBC05', // yellow
  INTERNAL_ERROR: '#EA4335', // red
};

const createSlackMessage = (build) => {
  const message = {
    attachments: [
      {
        color: STATUS_COLOR[build.status] || DEFAULT_COLOR,
        blocks: [
          {
            type: "section",
            text: {
              type: "mrkdwn",
              text: `*Cloud Build Trigger* - ${build.substitutions.TRIGGER_NAME}`,
            },
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "fields": [
              {
                "type": "mrkdwn",
                "text": `*Github Repo:*\n${build.substitutions.REPO_NAME}`,
              },
              {
                "type": "mrkdwn",
                "text": `*Branch:*\n${build.substitutions.BRANCH_NAME}`,
              },
              {
                "type": "mrkdwn",
                "text": `*Build Status:*\n${build.status}`,
              },
              {
                "type": "mrkdwn",
                "text": `*Build Logs:*\n<${build.logUrl}|Log URL>`,
              }
            ]
          },
          {
            "type": "divider"
          },
          {
            type: "section",
            text: {
              type: "mrkdwn",
              text: "Run Slack Slash command to approve and trigger consecutive Cloud build trigger."
            }
          }
        ],
      },
    ],
  };
  return message;
}

app.action('approve_button', async ({ ack }) => {
  await ack();
  // Update the message to reflect the action
});

app.action('approve_button', async ({ ack, say }) => {
  // Acknowledge action request
  await ack();
  await say('Terraform Plan Approved ✔️');
});

await context.chat.postMessage({
  text: 'Hello world!',
});

await context.chat.update({
  text: 'Hello world!',
  ts: '1405894322.002768',
});
