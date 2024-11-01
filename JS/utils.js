import { createRequire } from "node:module";

// making use of 'require' in the ES modules.
const require = createRequire(import.meta.url);


// the full credentials JSON file loaded in a single variable which can be used
// by other modules across the project.
export const CONFIG_CREDENTIALS = require('../credentials/ai-bot-credentials.json');


// return test or prod depending on the 
// boolean variable 'TESTING_MODE_ON' in the JSON credentials file
export function choose_tp(test, prod) {
    const test_mode_on = CONFIG_CREDENTIALS['TESTING-MODE-ON'];
    // console.log(test_mode_on);
    return (test_mode_on ? test : prod);
}
