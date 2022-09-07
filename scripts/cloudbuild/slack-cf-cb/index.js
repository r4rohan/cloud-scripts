const { IncomingWebhook } = require('@slack/webhook');
const url = 'https://hooks.slack.com/services/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';

const webhook = new IncomingWebhook(url);

// subscribeSlack is the main function called by Cloud Functions.
module.exports.subscribeSlack = (pubSubEvent, context) => {
  const build = eventToBuild(pubSubEvent.data);

  // Skip if the current status is not in the status list.
  // Add additional statuses to list if you'd like:
  // QUEUED, WORKING, SUCCESS, FAILURE,
  // INTERNAL_ERROR, TIMEOUT, CANCELLED
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
// createSlackMessage creates a message from a build object.
const createSlackMessage = (build) => {
  const message = {
    // text: `${build.substitutions.BRANCH_NAME._SLACK_MESSAGE}`,
    text: `${build.substitutions._SLACK_MESSAGE}`,
    mrkdwn: true,
    attachments: [
      {
        color: STATUS_COLOR[build.status] || DEFAULT_COLOR,
        text: `Trigger Name - ${build.substitutions.TRIGGER_NAME}`,
        text: `Repo - ${build.substitutions.REPO_NAME}`,
        text: `Branch - \`${build.substitutions.BRANCH_NAME}\``,
        fields: [{
          title: 'TRIGGER STATUS',
          value: build.status,
        },
        {
          title: 'CB LOGS',
          title_link: build.logUrl
        }],
      }
    ]
  };
  return message;
}
