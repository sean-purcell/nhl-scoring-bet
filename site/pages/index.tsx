import { Layout, Text, Code, Page, Link } from '@vercel/examples-ui'
import Head from 'next/head'

import fs from 'fs';
import path from 'path';

const GamesPlayed = ({ counts } : any) => (
  <div className="flex space-x-4">
    <div className="p-4"><Text variant="description">Games played:</Text></div>
    {counts.map((team) => (
      <div key={team[0]} className="p-4"><Text variant="description">{team[0]}: {team[1]}</Text></div>
    ))}
  </div>
);

const Game = ({ game } : any) => {
  const id = game.id;
  const title = game.names[0] + " - " + game.names[1];
  const scores = game.scores ? (game.scores[0] + " - " + game.scores[1]) : "";
  return (
    <div className="flex justify-between items-center border border-gray-100 shadow-md rounded-lg p-5">
      <div className="grid gap-2">
        <a
          href={`https://www.nhl.com/gamecenter/${id}`}
          target="_blank"
          rel="noreferrer noopener"
        >
          <h3 className="text-gray-900 text-lg hover:text-black font-semibold transition-all">
            {title}
          </h3>
        </a>
        {game.goals.map((goal, idx) => (
          <div key={idx} className="flex space-x-1 text-gray-500 text-sm">
            <p>{goal.period}</p>
            <p>{goal.time}</p>
            <p>-</p>
            <p>{goal.player} ({goal.goalsToDate})</p>
          </div>
        ))}
      </div>
      <h2 className="text-gray-800 text-lg">{scores}</h2>
    </div>
  )
};

export default function Home({ data }: { data: any }) {
  return (
    <Page>
      <section className="flex flex-col gap-6">
        <Text variant="h1">Goal Bet Tracker</Text>
        <Text variant="description">Tracking goals to settle a bet. The bet settles if any of the following pairs score on the same night:</Text>
        <Text variant="body">Draisaitl and Matthews</Text>
        <Text variant="body">Nylander and Point</Text>
        <Text variant="body">Kaprizov and Caufield</Text>
      </section>
      <section className="grid gap-6 mt-10 pt-10 border-t border-gray-300">
        <div className="flex flex-col gap-12">
          {data.map((date) => (
            <div key={date.date} className="flex flex-col gap-6">
              <div className="flex justify-between items-center">
                <Text variant="h2">{date.date}</Text>
                <GamesPlayed counts={date.played}/>
              </div>
              {date.games.map((game) => (
                <div key={game.id}><Game game={game}/></div>
              ))}
            </div>
          ))}
        </div>
      </section>
    </Page>
  )
}

export async function getStaticProps() {
  const dataPath = path.join(process.cwd(), 'public', 'data.json')
  const contents = fs.readFileSync(dataPath, 'utf8');
  const data = JSON.parse(contents);
  return {
    props: {
      data: data.reverse(),
    },
    revalidate: 60,
  };
}
