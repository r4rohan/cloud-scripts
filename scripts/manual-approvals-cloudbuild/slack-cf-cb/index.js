const { IncomingWebhook } = require('@slack/webhook');
const url = '[SLACK_TOKEN]';

const webhook = new IncomingWebhook(url);

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
  CANCELLED: '#808080' // grey
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
              text: `*Cloud Build* - ${build.substitutions.TRIGGER_NAME}`,
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
        ],
      },
    ],
  };
  return message;
}
