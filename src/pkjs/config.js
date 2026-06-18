// Clay configuration page for Tens. Each item's messageKey matches the keys
// declared in package.json and read in src/c/settings.c. Mirrors UserConfig.
module.exports = [
  { type: 'heading', defaultValue: 'Tens' },
  {
    type: 'section',
    items: [
      { type: 'heading', defaultValue: 'Day grid' },
      {
        type: 'toggle',
        messageKey: 'RAINBOW',
        label: 'Rainbow (spectral grid)',
        defaultValue: true,
      },
      {
        type: 'toggle',
        messageKey: 'DARK_MODE',
        label: 'Dark mode (black background)',
        defaultValue: true,
      },
      {
        type: 'toggle',
        messageKey: 'LAYOUT_4X6',
        label: 'Layout 4x6 (3x2 cells, vs 6x4)',
        defaultValue: true,
      },
      {
        type: 'toggle',
        messageKey: 'HOURS_HORIZONTAL',
        label: 'Hours fill horizontally (vs vertically)',
        defaultValue: true,
      },
      {
        type: 'toggle',
        messageKey: 'FILL_INVERT',
        label: 'Minute fill from far edge',
        defaultValue: false,
      },
      {
        type: 'toggle',
        messageKey: 'MISSING_STYLE',
        label: 'Fill missing parts (vs outline)',
        defaultValue: false,
      },
    ],
  },
  {
    type: 'section',
    items: [
      { type: 'heading', defaultValue: 'You' },
      {
        type: 'input',
        messageKey: 'BIRTH_YEAR',
        label: 'Birth year',
        attributes: { type: 'number', min: 1900, max: 2100 },
        defaultValue: '1990',
      },
      {
        type: 'input',
        messageKey: 'BIRTH_MONTH',
        label: 'Birth month (1-12)',
        attributes: { type: 'number', min: 1, max: 12 },
        defaultValue: '4',
      },
      {
        type: 'input',
        messageKey: 'BIRTH_DAY',
        label: 'Birth day (1-31)',
        attributes: { type: 'number', min: 1, max: 31 },
        defaultValue: '12',
      },
      {
        type: 'input',
        messageKey: 'LIFE_SPAN_YEARS',
        label: 'Life span (years)',
        attributes: { type: 'number', min: 1, max: 150 },
        defaultValue: '80',
      },
    ],
  },
  { type: 'submit', defaultValue: 'Save' },
];
